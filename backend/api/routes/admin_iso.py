"""
ISO Management routes for admin panel.
Allows CRUD operations on ISO entries, including overriding built-in ISOs.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

from api.database.session import get_db
from api.database.models import User
from api.routes.auth import get_current_admin_user
from core.models import OSInfo, OSCategory, Architecture
from core.os.base import get_registry

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
    is_custom: bool
    can_edit: bool


# In-memory storage for custom/overridden ISOs (in production, use database)
# This includes both user-added ISOs and overrides of built-in ISOs
custom_isos: List[dict] = []


def generate_iso_id(iso_data: ISOCreate) -> str:
    """Generate a unique ID for an ISO entry."""
    category = iso_data.category.lower()
    name = iso_data.name.lower().replace(" ", "-")
    version = iso_data.version.lower().replace(" ", "-")
    arch = iso_data.architecture.lower()
    return f"{category}_{name}_{version}_{arch}"


async def fetch_isos_from_category(category: OSCategory) -> List[dict]:
    """Fetch all ISOs from a specific category using the provider registry."""
    registry = get_registry()
    providers = registry.get_by_category(category)

    all_isos = []
    for provider in providers:
        try:
            os_list = await provider.fetch_available()
            for os_info in os_list:
                iso_id = f"{os_info.category.value}_{os_info.name.lower()}_{os_info.version.lower()}_{os_info.architecture.value}"
                all_isos.append({
                    "id": iso_id,
                    "name": os_info.name,
                    "version": os_info.version,
                    "category": os_info.category.value,
                    "architecture": os_info.architecture.value,
                    "language": os_info.language,
                    "url": os_info.url,
                    "size": os_info.size or 0,
                    "description": os_info.description,
                    "icon": os_info.icon,
                    "checksum": os_info.checksum,
                    "checksum_type": os_info.checksum_type,
                    "created_at": None,
                    "is_custom": False,
                    "can_edit": True  # All ISOs can now be edited
                })
        except Exception:
            pass

    return all_isos


@router.get("", response_model=List[ISOResponse])
async def list_all_isos(
    current_admin: User = Depends(get_current_admin_user),
    category: Optional[str] = None
):
    """
    List all ISOs (admin only).
    Can filter by category.
    Custom ISOs override built-in ISOs with the same ID.
    """
    # Use a dictionary to merge ISOs (custom overrides built-in)
    all_isos_dict = {}

    # Get built-in ISOs from providers
    for cat in [OSCategory.WINDOWS, OSCategory.LINUX, OSCategory.MACOS, OSCategory.BSD]:
        if category and cat.value != category.lower():
            continue
        try:
            cat_isos = await fetch_isos_from_category(cat)
            for iso in cat_isos:
                all_isos_dict[iso["id"]] = iso
        except Exception:
            pass

    # Add/override with custom ISOs
    for iso in custom_isos:
        if category and iso["category"] != category.lower():
            continue
        # Mark as editable and custom
        iso_with_flags = {
            **iso,
            "is_custom": True,
            "can_edit": True
        }
        all_isos_dict[iso["id"]] = iso_with_flags

    return list(all_isos_dict.values())


@router.post("", response_model=ISOResponse)
async def create_iso(
    iso_data: ISOCreate,
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Add a new custom ISO or override a built-in ISO (admin only).
    If an ISO with the same ID exists, it will be overridden.
    """
    iso_id = generate_iso_id(iso_data)

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
        "created_by": current_admin.username,
        "is_custom": True,
        "can_edit": True
    }

    # Check if ISO with this ID already exists in custom list and update or add
    existing_index = None
    for i, iso in enumerate(custom_isos):
        if iso["id"] == iso_id:
            existing_index = i
            break

    if existing_index is not None:
        # Update existing custom ISO
        custom_isos[existing_index] = new_iso
    else:
        # Add new custom ISO
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
    Can update both custom ISOs and create overrides for built-in ISOs.
    """
    # Check if this ISO already exists in custom list
    existing_index = None
    for i, iso in enumerate(custom_isos):
        if iso["id"] == iso_id:
            existing_index = i
            break

    if existing_index is not None:
        # Update existing custom ISO
        iso = custom_isos[existing_index]
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
        iso["is_custom"] = True
        iso["can_edit"] = True

        return iso
    else:
        # This is a built-in ISO that doesn't exist in custom list yet
        # Create a custom override for it
        # First, we need to fetch the original built-in ISO data to use as base
        for cat in [OSCategory.WINDOWS, OSCategory.LINUX, OSCategory.MACOS, OSCategory.BSD]:
            try:
                cat_isos = await fetch_isos_from_category(cat)
                for built_in_iso in cat_isos:
                    if built_in_iso["id"] == iso_id:
                        # Found the built-in ISO, create override
                        override_iso = {
                            **built_in_iso,
                            **{k: v for k, v in iso_data.dict().items() if v is not None},
                            "updated_at": datetime.utcnow().isoformat(),
                            "updated_by": current_admin.username,
                            "is_custom": True,
                            "can_edit": True
                        }
                        custom_isos.append(override_iso)
                        return override_iso
            except Exception:
                pass

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="ISO not found"
    )


@router.delete("/{iso_id}")
async def delete_iso(
    iso_id: str,
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Delete a custom ISO or remove an override (admin only).
    Cannot delete built-in ISOs, only removes custom overrides.
    """
    global custom_isos
    for i, iso in enumerate(custom_isos):
        if iso["id"] == iso_id:
            deleted_iso = custom_isos.pop(i)
            return {
                "message": f"ISO '{deleted_iso['name']}' deleted successfully. Built-in ISO will be used if available.",
                "id": iso_id
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Custom ISO not found (built-in ISOs cannot be deleted, only overridden)"
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
        "custom_count": len(custom_isos),
        "builtin_count": len(all_isos) - len([iso for iso in all_isos if iso.get("is_custom")])
    }

    # Count by category
    for iso in all_isos:
        cat = iso["category"]
        stats["by_category"][cat] = stats["by_category"].get(cat, 0) + 1

        # Count by architecture
        arch = iso["architecture"]
        stats["by_architecture"][arch] = stats["by_architecture"].get(arch, 0) + 1

    return stats
