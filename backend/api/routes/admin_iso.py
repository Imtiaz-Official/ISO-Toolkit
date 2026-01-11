"""
ISO Management routes for admin panel.
Allows CRUD operations on ISO entries, including overriding built-in ISOs.
Uses database storage for persistence across server restarts.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
import httpx
import json

from api.database.session import get_db
from api.database.models import User, ISOOverride
from api.routes.auth import get_current_admin_user
from core.models import OSInfo, OSCategory, Architecture
from core.os.base import get_registry
from core.os.windows import WindowsProvider
from core.os.linux import LinuxProvider
from core.os.macos import MacOSProvider
from core.os.bsd import BSDProvider

router = APIRouter(prefix="/api/admin/iso", tags=["Admin ISO Management"])

# Initialize providers on startup
_providers_initialized = False


def _init_providers():
    """Initialize OS providers."""
    global _providers_initialized
    if not _providers_initialized:
        registry = get_registry()
        registry.register(WindowsProvider())
        registry.register(LinuxProvider())
        registry.register(MacOSProvider())
        registry.register(BSDProvider())
        _providers_initialized = True


@router.on_event("startup")
async def startup():
    """Initialize providers on startup."""
    _init_providers()


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
    updated_at: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    is_custom: bool
    can_edit: bool
    is_enabled: bool = True


def generate_iso_id(iso_data: ISOCreate) -> str:
    """Generate a unique ID for an ISO entry."""
    category = iso_data.category.lower()
    name = iso_data.name.lower().replace(" ", "-")
    version = iso_data.version.lower().replace(" ", "-")
    arch = iso_data.architecture.lower()
    return f"{category}_{name}_{version}_{arch}"


async def fetch_isos_from_category(category: OSCategory, db: Session) -> List[dict]:
    """Fetch all ISOs from a specific category using the provider registry."""
    _init_providers()
    registry = get_registry()
    providers = registry.get_by_category(category)

    all_isos = []

    # Get database overrides for this category
    overrides = db.query(ISOOverride).filter(
        ISOOverride.category == category.value,
        ISOOverride.is_enabled == True
    ).all()

    # Create a lookup dict for overrides
    override_map = {override.iso_id: override for override in overrides}

    for provider in providers:
        try:
            os_list = await provider.fetch_available()
            for os_info in os_list:
                iso_id = f"{os_info.category.value}_{os_info.name.lower()}_{os_info.version.lower()}_{os_info.architecture.value}"

                # Check if there's a database override
                if iso_id in override_map:
                    override = override_map[iso_id]
                    all_isos.append(override.to_dict())
                else:
                    # Use built-in data
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
                        "updated_at": None,
                        "created_by": None,
                        "updated_by": None,
                        "is_custom": False,
                        "is_enabled": True,
                        "can_edit": True
                    })
        except Exception:
            pass

    return all_isos


@router.get("", response_model=List[ISOResponse])
async def list_all_isos(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    category: Optional[str] = None,
    include_disabled: bool = False
):
    """
    List all ISOs (admin only).
    Can filter by category.
    Database overrides take precedence over built-in ISOs.
    """
    all_isos_dict = {}

    # Get built-in ISOs from providers (with overrides applied)
    for cat in [OSCategory.WINDOWS, OSCategory.LINUX, OSCategory.MACOS, OSCategory.BSD]:
        if category and cat.value != category.lower():
            continue
        try:
            cat_isos = await fetch_isos_from_category(cat, db)
            for iso in cat_isos:
                if include_disabled or iso.get("is_enabled", True):
                    all_isos_dict[iso["id"]] = iso
        except Exception:
            pass

    return list(all_isos_dict.values())


@router.post("", response_model=ISOResponse)
async def create_iso(
    iso_data: ISOCreate,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Add a new custom ISO or override a built-in ISO (admin only).
    If an ISO with the same ID exists, it will be updated.
    """
    iso_id = generate_iso_id(iso_data)

    # Check if already exists
    existing = db.query(ISOOverride).filter(ISOOverride.iso_id == iso_id).first()

    if existing:
        # Update existing
        existing.name = iso_data.name
        existing.version = iso_data.version
        existing.category = iso_data.category
        existing.architecture = iso_data.architecture
        existing.language = iso_data.language
        existing.url = iso_data.url
        existing.size = iso_data.size
        existing.description = iso_data.description
        existing.icon = iso_data.icon
        existing.checksum = iso_data.checksum
        existing.checksum_type = iso_data.checksum_type
        existing.updated_at = datetime.utcnow()
        existing.updated_by = current_admin.username
        existing.is_enabled = True

        db.commit()
        db.refresh(existing)
        return existing.to_dict()
    else:
        # Create new
        new_override = ISOOverride(
            iso_id=iso_id,
            name=iso_data.name,
            version=iso_data.version,
            category=iso_data.category,
            architecture=iso_data.architecture,
            language=iso_data.language,
            url=iso_data.url,
            size=iso_data.size,
            description=iso_data.description,
            icon=iso_data.icon,
            checksum=iso_data.checksum,
            checksum_type=iso_data.checksum_type,
            created_by=current_admin.username,
            is_enabled=True
        )

        db.add(new_override)
        db.commit()
        db.refresh(new_override)
        return new_override.to_dict()


@router.put("/{iso_id}", response_model=ISOResponse)
async def update_iso(
    iso_id: str,
    iso_data: ISOUpdate,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing ISO (admin only).
    Can update both custom ISOs and create overrides for built-in ISOs.
    """
    # Check if this ISO already exists in database
    existing = db.query(ISOOverride).filter(ISOOverride.iso_id == iso_id).first()

    if existing:
        # Update existing override
        if iso_data.name is not None:
            existing.name = iso_data.name
        if iso_data.version is not None:
            existing.version = iso_data.version
        if iso_data.category is not None:
            existing.category = iso_data.category
        if iso_data.architecture is not None:
            existing.architecture = iso_data.architecture
        if iso_data.language is not None:
            existing.language = iso_data.language
        if iso_data.url is not None:
            existing.url = iso_data.url
        if iso_data.size is not None:
            existing.size = iso_data.size
        if iso_data.description is not None:
            existing.description = iso_data.description
        if iso_data.icon is not None:
            existing.icon = iso_data.icon
        if iso_data.checksum is not None:
            existing.checksum = iso_data.checksum
        if iso_data.checksum_type is not None:
            existing.checksum_type = iso_data.checksum_type

        existing.updated_at = datetime.utcnow()
        existing.updated_by = current_admin.username

        db.commit()
        db.refresh(existing)
        return existing.to_dict()
    else:
        # This is a built-in ISO that doesn't exist in database yet
        # Create a database override for it
        # First, we need to fetch the original built-in ISO data to use as base
        for cat in [OSCategory.WINDOWS, OSCategory.LINUX, OSCategory.MACOS, OSCategory.BSD]:
            try:
                cat_isos = await fetch_isos_from_category(cat, db)
                for built_in_iso in cat_isos:
                    if built_in_iso["id"] == iso_id and not built_in_iso.get("is_custom"):
                        # Found the built-in ISO, create override
                        new_override = ISOOverride(
                            iso_id=iso_id,
                            name=built_in_iso["name"],
                            version=built_in_iso["version"],
                            category=built_in_iso["category"],
                            architecture=built_in_iso["architecture"],
                            language=built_in_iso["language"],
                            url=built_in_iso["url"],
                            size=built_in_iso.get("size", 0),
                            description=built_in_iso.get("description"),
                            icon=built_in_iso.get("icon"),
                            checksum=built_in_iso.get("checksum"),
                            checksum_type=built_in_iso.get("checksum_type"),
                            created_by=current_admin.username,
                            is_enabled=True
                        )

                        # Apply updates
                        if iso_data.name is not None:
                            new_override.name = iso_data.name
                        if iso_data.version is not None:
                            new_override.version = iso_data.version
                        if iso_data.url is not None:
                            new_override.url = iso_data.url
                        if iso_data.size is not None:
                            new_override.size = iso_data.size
                        if iso_data.description is not None:
                            new_override.description = iso_data.description
                        if iso_data.icon is not None:
                            new_override.icon = iso_data.icon

                        db.add(new_override)
                        db.commit()
                        db.refresh(new_override)
                        return new_override.to_dict()
            except Exception:
                pass

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="ISO not found"
    )


@router.delete("/{iso_id}")
async def delete_iso(
    iso_id: str,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete a custom ISO or remove an override (admin only).
    Cannot delete built-in ISOs, only removes custom overrides.
    """
    override = db.query(ISOOverride).filter(ISOOverride.iso_id == iso_id).first()

    if override:
        db.delete(override)
        db.commit()
        return {
            "message": f"ISO '{override.name}' deleted successfully. Built-in ISO will be used if available.",
            "id": iso_id
        }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Custom ISO not found (built-in ISOs cannot be deleted, only overridden)"
    )


@router.get("/stats", response_model=dict)
async def get_iso_stats(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get ISO statistics (admin only).
    """
    all_isos = await list_all_isos(current_admin, db, None)

    # Get override count from database
    override_count = db.query(ISOOverride).count()

    stats = {
        "total_count": len(all_isos),
        "by_category": {},
        "by_architecture": {},
        "custom_count": override_count,
        "builtin_count": len(all_isos) - override_count
    }

    # Count by category
    for iso in all_isos:
        cat = iso["category"]
        stats["by_category"][cat] = stats["by_category"].get(cat, 0) + 1

        # Count by architecture
        arch = iso["architecture"]
        stats["by_architecture"][arch] = stats["by_architecture"].get(arch, 0) + 1

    return stats


# ============================================================================
# URL Validation and Testing
# ============================================================================

class URLValidationRequest(BaseModel):
    url: str
    timeout: int = 10  # seconds
    check_size: bool = True


class URLValidationResponse(BaseModel):
    url: str
    is_valid: bool
    status_code: Optional[int] = None
    content_length: Optional[int] = None
    content_type: Optional[str] = None
    supports_resume: bool = False
    error_message: Optional[str] = None
    redirect_url: Optional[str] = None
    requires_bypass: bool = False


@router.post("/validate-url", response_model=URLValidationResponse)
async def validate_iso_url(
    request: URLValidationRequest,
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Validate if a URL is accessible and get file information.
    Useful for testing URLs before adding them to the database.
    Detects if URL requires Cloudflare/bypass.
    """
    try:
        async with httpx.AsyncClient(timeout=request.timeout, follow_redirects=True) as client:
            # First try HEAD request to check without downloading
            try:
                response = await client.head(request.url)
                status_code = response.status_code
                content_length = response.headers.get("content-length")
                content_type = response.headers.get("content-type")
                supports_resume = response.headers.get("accept-ranges") == "bytes"
                redirect_url = str(response.url) if str(response.url) != request.url else None

                # Check if response contains Cloudflare or protection page
                requires_bypass = False
                if content_type and "text/html" in content_type:
                    requires_bypass = True

                if content_length:
                    try:
                        content_length = int(content_length)
                    except ValueError:
                        content_length = None

                return URLValidationResponse(
                    url=request.url,
                    is_valid=status_code < 400 and not requires_bypass,
                    status_code=status_code,
                    content_length=content_length,
                    content_type=content_type,
                    supports_resume=supports_resume,
                    redirect_url=redirect_url,
                    requires_bypass=requires_bypass,
                    error_message="URL returns HTML (may require Cloudflare bypass)" if requires_bypass else None
                )
            except Exception as e:
                # If HEAD fails, try GET (some servers don't support HEAD)
                try:
                    response = await client.get(request.url, headers={"Range": "bytes=0-1023"})
                    status_code = response.status_code
                    content_length = response.headers.get("content-length")
                    content_type = response.headers.get("content-type")
                    supports_resume = response.headers.get("accept-ranges") == "bytes"
                    redirect_url = str(response.url) if str(response.url) != request.url else None

                    requires_bypass = False
                    if content_type and "text/html" in content_type:
                        requires_bypass = True

                    if content_length:
                        try:
                            content_length = int(content_length)
                        except ValueError:
                            content_length = None

                    return URLValidationResponse(
                        url=request.url,
                        is_valid=status_code < 400 and not requires_bypass,
                        status_code=status_code,
                        content_length=content_length,
                        content_type=content_type,
                        supports_resume=supports_resume,
                        redirect_url=redirect_url,
                        requires_bypass=requires_bypass,
                        error_message="URL returns HTML (may require Cloudflare bypass)" if requires_bypass else None
                    )
                except Exception as e2:
                    return URLValidationResponse(
                        url=request.url,
                        is_valid=False,
                        error_message=str(e2)
                    )
    except Exception as e:
        return URLValidationResponse(
            url=request.url,
            is_valid=False,
            error_message=str(e)
        )


# ============================================================================
# Bulk Operations
# ============================================================================

class BulkUpdateRequest(BaseModel):
    iso_ids: List[str]
    updates: ISOUpdate


class BulkDeleteRequest(BaseModel):
    iso_ids: List[str]


class BulkEnableDisableRequest(BaseModel):
    iso_ids: List[str]
    is_enabled: bool


@router.post("/bulk/update", response_model=List[ISOResponse])
async def bulk_update_isos(
    request: BulkUpdateRequest,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update multiple ISOs at once (admin only).
    Creates database overrides for all specified ISOs.
    """
    results = []

    for iso_id in request.iso_ids:
        existing = db.query(ISOOverride).filter(ISOOverride.iso_id == iso_id).first()

        if existing:
            # Update existing override
            if request.updates.name is not None:
                existing.name = request.updates.name
            if request.updates.version is not None:
                existing.version = request.updates.version
            if request.updates.category is not None:
                existing.category = request.updates.category
            if request.updates.architecture is not None:
                existing.architecture = request.updates.architecture
            if request.updates.language is not None:
                existing.language = request.updates.language
            if request.updates.url is not None:
                existing.url = request.updates.url
            if request.updates.size is not None:
                existing.size = request.updates.size
            if request.updates.description is not None:
                existing.description = request.updates.description
            if request.updates.icon is not None:
                existing.icon = request.updates.icon
            if request.updates.checksum is not None:
                existing.checksum = request.updates.checksum
            if request.updates.checksum_type is not None:
                existing.checksum_type = request.updates.checksum_type

            existing.updated_at = datetime.utcnow()
            existing.updated_by = current_admin.username

            db.commit()
            db.refresh(existing)
            results.append(existing.to_dict())
        else:
            # Find built-in ISO and create override
            for cat in [OSCategory.WINDOWS, OSCategory.LINUX, OSCategory.MACOS, OSCategory.BSD]:
                try:
                    cat_isos = await fetch_isos_from_category(cat, db)
                    for built_in_iso in cat_isos:
                        if built_in_iso["id"] == iso_id and not built_in_iso.get("is_custom"):
                            new_override = ISOOverride(
                                iso_id=iso_id,
                                name=built_in_iso["name"],
                                version=built_in_iso["version"],
                                category=built_in_iso["category"],
                                architecture=built_in_iso["architecture"],
                                language=built_in_iso["language"],
                                url=built_in_iso["url"],
                                size=built_in_iso.get("size", 0),
                                description=built_in_iso.get("description"),
                                icon=built_in_iso.get("icon"),
                                checksum=built_in_iso.get("checksum"),
                                checksum_type=built_in_iso.get("checksum_type"),
                                created_by=current_admin.username,
                                is_enabled=True
                            )

                            # Apply updates
                            if request.updates.name is not None:
                                new_override.name = request.updates.name
                            if request.updates.version is not None:
                                new_override.version = request.updates.version
                            if request.updates.url is not None:
                                new_override.url = request.updates.url
                            if request.updates.size is not None:
                                new_override.size = request.updates.size
                            if request.updates.description is not None:
                                new_override.description = request.updates.description
                            if request.updates.icon is not None:
                                new_override.icon = request.updates.icon

                            db.add(new_override)
                            db.commit()
                            db.refresh(new_override)
                            results.append(new_override.to_dict())
                            break
                except Exception:
                    pass

    return results


@router.post("/bulk/delete")
async def bulk_delete_isos(
    request: BulkDeleteRequest,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete multiple custom ISOs at once (admin only).
    Only removes custom overrides, not built-in ISOs.
    """
    deleted_count = 0
    deleted_names = []

    for iso_id in request.iso_ids:
        override = db.query(ISOOverride).filter(ISOOverride.iso_id == iso_id).first()
        if override:
            deleted_names.append(override.name)
            db.delete(override)
            deleted_count += 1

    db.commit()

    return {
        "message": f"Deleted {deleted_count} ISO(s) successfully",
        "deleted_count": deleted_count,
        "deleted_names": deleted_names
    }


@router.post("/bulk/toggle")
async def bulk_toggle_isos(
    request: BulkEnableDisableRequest,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Enable or disable multiple ISOs at once (admin only).
    """
    updated_count = 0

    for iso_id in request.iso_ids:
        override = db.query(ISOOverride).filter(ISOOverride.iso_id == iso_id).first()
        if override:
            override.is_enabled = request.is_enabled
            override.updated_at = datetime.utcnow()
            override.updated_by = current_admin.username
            updated_count += 1

    db.commit()

    return {
        "message": f"{'Enabled' if request.is_enabled else 'Disabled'} {updated_count} ISO(s) successfully",
        "updated_count": updated_count
    }


# ============================================================================
# Import/Export
# ============================================================================

@router.get("/export")
async def export_isos(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    category: Optional[str] = None,
    include_builtin: bool = False
):
    """
    Export all ISOs as JSON (admin only).
    Useful for backup or migration.
    """
    all_isos = await list_all_isos(current_admin, db, category, include_disabled=False)

    export_data = {
        "exported_at": datetime.utcnow().isoformat(),
        "exported_by": current_admin.username,
        "total_count": len(all_isos),
        "isos": []
    }

    for iso in all_isos:
        if include_builtin or iso.get("is_custom", False):
            export_data["isos"].append({
                "name": iso["name"],
                "version": iso["version"],
                "category": iso["category"],
                "architecture": iso["architecture"],
                "language": iso["language"],
                "url": iso["url"],
                "size": iso["size"],
                "description": iso.get("description"),
                "icon": iso.get("icon"),
                "checksum": iso.get("checksum"),
                "checksum_type": iso.get("checksum_type"),
            })

    export_data["exported_count"] = len(export_data["isos"])

    return export_data


class ImportRequest(BaseModel):
    isos: List[ISOCreate]
    mode: str = "update"  # "update", "replace", or "skip"


@router.post("/import", response_model=Dict[str, Any])
async def import_isos(
    request: ImportRequest,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Import ISOs from JSON (admin only).
    Mode options:
    - "update": Update existing ISOs, create new ones (default)
    - "replace": Replace all existing ISOs with imported ones
    - "skip": Skip existing ISOs, only create new ones
    """
    created_count = 0
    updated_count = 0
    skipped_count = 0
    errors = []

    if request.mode == "replace":
        # Delete all existing overrides first
        db.query(ISOOverride).delete()
        db.commit()

    for iso_data in request.isos:
        try:
            iso_id = generate_iso_id(iso_data)
            existing = db.query(ISOOverride).filter(ISOOverride.iso_id == iso_id).first()

            if existing:
                if request.mode == "skip":
                    skipped_count += 1
                    continue

                # Update existing
                existing.name = iso_data.name
                existing.version = iso_data.version
                existing.category = iso_data.category
                existing.architecture = iso_data.architecture
                existing.language = iso_data.language
                existing.url = iso_data.url
                existing.size = iso_data.size
                existing.description = iso_data.description
                existing.icon = iso_data.icon
                existing.checksum = iso_data.checksum
                existing.checksum_type = iso_data.checksum_type
                existing.updated_at = datetime.utcnow()
                existing.updated_by = current_admin.username
                existing.is_enabled = True

                updated_count += 1
            else:
                # Create new
                new_override = ISOOverride(
                    iso_id=iso_id,
                    name=iso_data.name,
                    version=iso_data.version,
                    category=iso_data.category,
                    architecture=iso_data.architecture,
                    language=iso_data.language,
                    url=iso_data.url,
                    size=iso_data.size,
                    description=iso_data.description,
                    icon=iso_data.icon,
                    checksum=iso_data.checksum,
                    checksum_type=iso_data.checksum_type,
                    created_by=current_admin.username,
                    is_enabled=True
                )

                db.add(new_override)
                created_count += 1

        except Exception as e:
            errors.append({
                "iso": iso_data.name if hasattr(iso_data, 'name') else 'unknown',
                "error": str(e)
            })

    db.commit()

    return {
        "message": f"Import completed: {created_count} created, {updated_count} updated, {skipped_count} skipped",
        "created": created_count,
        "updated": updated_count,
        "skipped": skipped_count,
        "errors": errors
    }


# ============================================================================
# Quick Actions
# ============================================================================

class QuickUpdateURLRequest(BaseModel):
    iso_id: str
    new_url: str
    verify_url: bool = True  # Validate URL before updating


@router.post("/quick-update-url", response_model=ISOResponse)
async def quick_update_url(
    request: QuickUpdateURLRequest,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Quickly update just the URL of an ISO (admin only).
    Optionally validates the URL before updating.
    """
    validation = None
    # Verify URL if requested
    if request.verify_url:
        validation = await validate_iso_url(
            URLValidationRequest(url=request.new_url, timeout=10),
            current_admin
        )

    # Check if override exists
    existing = db.query(ISOOverride).filter(ISOOverride.iso_id == request.iso_id).first()

    if existing:
        existing.url = request.new_url
        existing.updated_at = datetime.utcnow()
        existing.updated_by = current_admin.username

        # Update size if validation returned one
        if validation and validation.content_length:
            existing.size = validation.content_length

        db.commit()
        db.refresh(existing)
        return existing.to_dict()
    else:
        # Find built-in ISO and create override
        for cat in [OSCategory.WINDOWS, OSCategory.LINUX, OSCategory.MACOS, OSCategory.BSD]:
            try:
                cat_isos = await fetch_isos_from_category(cat, db)
                for built_in_iso in cat_isos:
                    if built_in_iso["id"] == request.iso_id and not built_in_iso.get("is_custom"):
                        new_override = ISOOverride(
                            iso_id=request.iso_id,
                            name=built_in_iso["name"],
                            version=built_in_iso["version"],
                            category=built_in_iso["category"],
                            architecture=built_in_iso["architecture"],
                            language=built_in_iso["language"],
                            url=request.new_url,
                            size=validation.content_length if validation and validation.content_length else built_in_iso.get("size", 0),
                            description=built_in_iso.get("description"),
                            icon=built_in_iso.get("icon"),
                            checksum=built_in_iso.get("checksum"),
                            checksum_type=built_in_iso.get("checksum_type"),
                            created_by=current_admin.username,
                            is_enabled=True
                        )

                        db.add(new_override)
                        db.commit()
                        db.refresh(new_override)
                        return new_override.to_dict()
            except Exception:
                pass

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="ISO not found"
    )


@router.post("/reset/{iso_id}")
async def reset_iso_to_builtin(
    iso_id: str,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Reset a custom ISO back to built-in defaults (admin only).
    Removes the database override.
    """
    override = db.query(ISOOverride).filter(ISOOverride.iso_id == iso_id).first()

    if override:
        name = override.name
        db.delete(override)
        db.commit()

        return {
            "message": f"ISO '{name}' reset to built-in defaults",
            "iso_id": iso_id
        }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Custom ISO not found (already using built-in defaults)"
    )


