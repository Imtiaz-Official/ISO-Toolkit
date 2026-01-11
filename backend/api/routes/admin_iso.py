"""
ISO Management routes for admin panel.
Allows CRUD operations on ISO entries.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

from api.database.session import get_db
from api.database.models import User
from api.routes.os import get_all_os, get_os_by_category
from api.routes.auth import get_current_admin_user
from core.models import OSInfo, OSCategory, Architecture

router = APIRouter(prefix="/api/admin/iso", tags=["Admin ISO Management"])


class ISOCreate(BaseModel):
    name: str
    version: str
    category: str  # WINDOWS, LINUX, MACOS, BSD, OTHER
    architecture: str  # X64, X86, ARM64, ARM, RISCV64, UNIVERSAL
    language: str
    url: str
    size: int
    description: Optional[str] = None
    icon: Optional[str] = None
    checksum: Optional[str] = None
    checksum_type: Optional[str] = None


class ISOUpdate(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None
    category: Optional[str] = None
    architecture: Optional[str] = None
    language: Optional[str] = None
    url: Optional[str] = None
    size: Optional[int] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    checksum: Optional[str] = None
    checksum_type: Optional[str] = None


class ISOResponse(BaseModel):
    id: str
    name: str
    version: str
    category: str
    architecture: str
    language: str
    url: str
    size: int
    description: Optional[str] = None
    icon: Optional[str] = None
    checksum: Optional[str] = None
    checksum_type: Optional[str] = None
    created_at: Optional[str] = None


# In-memory storage for custom ISOs (in production, use database)
custom_isos: List[dict] = []


def generate_iso_id(iso_data: ISOCreate) -> str:
    """Generate a unique ID for an ISO entry."""
    category = iso_data.category.lower()
    name = iso_data.name.lower().replace(" ", "-")
    version = iso_data.version.lower().replace(" ", "-")
    arch = iso_data.architecture.lower()
    return f"{category}_{name}_{version}_{arch}"


@router.get("", response_model=List[ISOResponse])
async def list_all_isos(
    current_admin: User = Depends(get_current_admin_user),
    category: Optional[str] = None
):
    """
    List all ISOs (admin only).
    Can filter by category.
    """
    all_isos = []

    # Get built-in ISOs from providers
    for cat in [OSCategory.WINDOWS, OSCategory.LINUX, OSCategory.MACOS, OSCategory.BSD]:
        if category and cat.value != category:
            continue
        try:
            cat_isos = await get_os_by_category(cat)
            all_isos.extend([{
                "id": iso.id,
                "name": iso.name,
                "version": iso.version,
                "category": iso.category.value,
                "architecture": iso.architecture.value,
                "language": iso.language,
                "url": iso.url,
                "size": iso.size or 0,
                "description": iso.description,
                "icon": iso.icon,
                "checksum": iso.checksum,
                "checksum_type": iso.checksum_type,
                "created_at": None,
                "is_custom": False
            } for iso in cat_isos])
        except Exception:
            pass

    # Add custom ISOs
    for iso in custom_isos:
        if category and iso["category"] != category:
            continue
        all_isos.append({
            **iso,
            "is_custom": True
        })

    return all_isos


@router.post("", response_model=ISOResponse)
async def create_iso(
    iso_data: ISOCreate,
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Add a new custom ISO (admin only).
    """
    iso_id = generate_iso_id(iso_data)

    # Check if ISO with this ID already exists
    for iso in custom_isos:
        if iso["id"] == iso_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ISO with this configuration already exists"
            )

    new_iso = {
        "id": iso_id,
        "name": iso_data.name,
        "version": iso_data.version,
        "category": iso_data.category,
        "architecture": iso_data.architecture,
        "language": iso_data.language,
        "url": iso_data.url,
        "size": iso_data.size,
        "description": iso_data.description,
        "icon": iso_data.icon or "💿",
        "checksum": iso_data.checksum,
        "checksum_type": iso_data.checksum_type,
        "created_at": datetime.utcnow().isoformat(),
        "created_by": current_admin.username
    }

    custom_isos.append(new_iso)

    return new_iso


@router.put("/{iso_id}", response_model=ISOResponse)
async def update_iso(
    iso_id: str,
    iso_data: ISOUpdate,
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Update an existing ISO (admin only).
    Only custom ISOs can be modified.
    """
    for i, iso in enumerate(custom_isos):
        if iso["id"] == iso_id:
            # Update fields
            if iso_data.name is not None:
                iso["name"] = iso_data.name
            if iso_data.version is not None:
                iso["version"] = iso_data.version
            if iso_data.category is not None:
                iso["category"] = iso_data.category
            if iso_data.architecture is not None:
                iso["architecture"] = iso_data.architecture
            if iso_data.language is not None:
                iso["language"] = iso_data.language
            if iso_data.url is not None:
                iso["url"] = iso_data.url
            if iso_data.size is not None:
                iso["size"] = iso_data.size
            if iso_data.description is not None:
                iso["description"] = iso_data.description
            if iso_data.icon is not None:
                iso["icon"] = iso_data.icon
            if iso_data.checksum is not None:
                iso["checksum"] = iso_data.checksum
            if iso_data.checksum_type is not None:
                iso["checksum_type"] = iso_data.checksum_type

            iso["updated_at"] = datetime.utcnow().isoformat()
            iso["updated_by"] = current_admin.username

            return iso

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Custom ISO not found"
    )


@router.delete("/{iso_id}")
async def delete_iso(
    iso_id: str,
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Delete a custom ISO (admin only).
    Only custom ISOs can be deleted.
    """
    global custom_isos
    for i, iso in enumerate(custom_isos):
        if iso["id"] == iso_id:
            deleted_iso = custom_isos.pop(i)
            return {
                "message": f"ISO '{deleted_iso['name']}' deleted successfully",
                "id": iso_id
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Custom ISO not found"
    )


@router.get("/stats", response_model=dict)
async def get_iso_stats(
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Get ISO statistics (admin only).
    """
    all_isos = await list_all_isos(current_admin, None)

    stats = {
        "total_count": len(all_isos),
        "by_category": {},
        "by_architecture": {},
        "custom_count": len(custom_isos)
    }

    # Count by category
    for iso in all_isos:
        cat = iso["category"]
        stats["by_category"][cat] = stats["by_category"].get(cat, 0) + 1

        # Count by architecture
        arch = iso["architecture"]
        stats["by_architecture"][arch] = stats["by_architecture"].get(arch, 0) + 1

    return stats
