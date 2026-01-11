"""
API routes for OS listings and browsing.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Union, Optional
import asyncio
from sqlalchemy.orm import Session

from api.models.schemas import (
    OSInfoResponse,
    OSCategoryResponse,
    LinuxSubcategoryResponse,
    Architecture,
)
from api.database.session import get_db
from api.database.models import ISOOverride
from core.os.base import get_registry
from core.os.windows import WindowsProvider
from core.os.linux import LinuxProvider
from core.os.macos import MacOSProvider
from core.os.bsd import BSDProvider
from core.models import OSCategory

router = APIRouter(prefix="/api/os", tags=["OS"])

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


@router.get("/categories", response_model=List[OSCategoryResponse])
async def get_categories() -> List[OSCategoryResponse]:
    """
    Get all available OS categories.

    Returns:
        List of OS categories with counts
    """
    _init_providers()

    registry = get_registry()
    all_providers = registry.get_all_providers()
    print(f"DEBUG: Total providers registered: {len(all_providers)}")

    categories = [
        OSCategoryResponse(
            category=OSCategory.WINDOWS,
            name="Windows",
            icon="🪟",
            count=0,  # Will be filled
        ),
        OSCategoryResponse(
            category=OSCategory.LINUX,
            name="Linux",
            icon="🐧",
            count=0,
        ),
        OSCategoryResponse(
            category=OSCategory.MACOS,
            name="macOS",
            icon="🍎",
            count=0,
        ),
        OSCategoryResponse(
            category=OSCategory.BSD,
            name="BSD",
            icon="🐡",
            count=0,
        ),
    ]

    # Get counts from providers
    for category_response in categories:
        providers = registry.get_by_category(category_response.category)
        total_count = 0
        for provider in providers:
            try:
                os_list = await provider.fetch_available()
                total_count += len(os_list)
            except Exception:
                pass
        category_response.count = total_count

    return categories


@router.get("/linux/subcategories", response_model=List[LinuxSubcategoryResponse])
async def get_linux_subcategories() -> List[LinuxSubcategoryResponse]:
    """
    Get all Linux distribution subcategories.

    Returns:
        List of Linux distribution subcategories with counts
    """
    _init_providers()

    registry = get_registry()
    providers = registry.get_by_category(OSCategory.LINUX)

    all_subcategories = {}

    for provider in providers:
        try:
            os_list = await provider.fetch_available()
            for os_info in os_list:
                subcategory = os_info.subcategory or os_info.name
                if subcategory not in all_subcategories:
                    all_subcategories[subcategory] = {
                        "subcategory": subcategory,
                        "name": subcategory,
                        "icon": os_info.icon or "🐧",
                        "count": 0
                    }
                all_subcategories[subcategory]["count"] += 1
        except Exception:
            pass

    # Popularity ranking for Linux distributions (most popular first)
    popularity_order = [
        # Ubuntu Family
        "Ubuntu", "Linux Mint", "Linux Mint Cinnamon", "Linux Mint MATE", "Linux Mint XFCE",
        "Kubuntu", "Xubuntu", "Lubuntu", "Pop!_OS", "Ubuntu MATE",
        "Ubuntu Studio", "Ubuntu Budgie", "Ubuntu Cinnamon", "Edubuntu", "KDE neon",
        # Fedora & RHEL Family
        "Fedora", "Fedora Workstation", "Fedora KDE Plasma", "Fedora XFCE",
        "Fedora Server", "Fedora Cinnamon", "Fedora LXQt", "Fedora ARM",
        "Rocky Linux", "AlmaLinux", "CentOS Stream", "RHEL", "Oracle Linux",
        # Debian Family
        "Debian", "Raspberry Pi OS",
        # Arch Family
        "Arch Linux", "Manjaro", "EndeavourOS", "Garuda Linux", "Artix Linux", "ArcoLinux",
        # Major Independent Distros
        "elementary OS", "Zorin OS", "MX Linux", "Solus", "NixOS",
        "openSUSE", "deepin", "antiX", "Void Linux", "Gentoo", "Slackware",
        # Security/Privacy
        "Kali Linux", "Parrot OS", "Tails",
        # Light/Minimal
        "Puppy Linux", "Bodhi Linux", "Q4OS", "PCLinuxOS", "Alpine Linux",
        "DietPi", "Clear Linux", "Mageia",
        # ARM/SBC
        "LibreELEC",
        # Cloud/Enterprise
        "Amazon Linux",
        # Others
        "BigLinux", "RebeccaBlackOS",
    ]

    # Sort by popularity, with unknown distributions at the end (sorted alphabetically)
    def get_popularity_rank(name: str) -> int:
        try:
            return popularity_order.index(name)
        except ValueError:
            return 9999  # Unknown distributions go to the end

    sorted_subcategories = sorted(
        all_subcategories.values(),
        key=lambda x: (get_popularity_rank(x["name"]), x["name"])
    )
    return [LinuxSubcategoryResponse(**sc) for sc in sorted_subcategories]


@router.get("/windows/subcategories", response_model=List[LinuxSubcategoryResponse])
async def get_windows_subcategories() -> List[LinuxSubcategoryResponse]:
    """
    Get all Windows version subcategories.

    Returns:
        List of Windows version subcategories with counts
    """
    _init_providers()

    registry = get_registry()
    providers = registry.get_by_category(OSCategory.WINDOWS)

    all_subcategories = {}

    for provider in providers:
        try:
            os_list = await provider.fetch_available()
            for os_info in os_list:
                subcategory = os_info.subcategory or os_info.name
                if subcategory not in all_subcategories:
                    all_subcategories[subcategory] = {
                        "subcategory": subcategory,
                        "name": subcategory,
                        "icon": os_info.icon or "🪟",
                        "count": 0
                    }
                all_subcategories[subcategory]["count"] += 1
        except Exception:
            pass

    # Windows versions in release order (newest first)
    windows_order = [
        "Windows 11",
        "Windows 10",
        "Windows 8.1",
        "Windows 7",
        "Windows XP",
    ]

    # Sort by Windows release order (newest first)
    def get_windows_order(name: str) -> int:
        try:
            return windows_order.index(name)
        except ValueError:
            return 9999  # Unknown versions go to the end

    sorted_subcategories = sorted(
        all_subcategories.values(),
        key=lambda x: get_windows_order(x["name"])
    )
    return [LinuxSubcategoryResponse(**sc) for sc in sorted_subcategories]


@router.get("/{category}", response_model=List[OSInfoResponse])
async def get_os_by_category(
    category: str,
    architecture: Architecture | None = None,
    language: str | None = None,
    subcategory: str | None = None,
    db: Session = Depends(get_db),
) -> List[OSInfoResponse]:
    """
    Get available OS for a specific category.
    Database overrides take precedence over built-in ISOs.

    Args:
        category: OS category (windows, linux, macos, bsd)
        architecture: Filter by architecture (optional)
        language: Filter by language (optional)
        subcategory: Filter by subcategory for Linux (optional)

    Returns:
        List of available OS
    """
    _init_providers()

    # Convert string to OSCategory enum
    try:
        category_enum = OSCategory(category.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category: {category}. Valid options: windows, linux, macos, bsd"
        )

    registry = get_registry()
    providers = registry.get_by_category(category_enum)

    # Get database overrides for this category
    overrides = db.query(ISOOverride).filter(
        ISOOverride.category == category_enum.value,
        ISOOverride.is_enabled == True
    ).all()

    # Create a lookup dict for overrides
    override_map = {override.iso_id: override for override in overrides}

    all_os = []
    for provider in providers:
        try:
            os_list = await provider.fetch_available(
                architecture=architecture,
                language=language,
            )
            all_os.extend(os_list)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching OS: {str(e)}")

    # Apply database overrides to built-in ISOs and add custom ISOs
    merged_os = {}
    for os_info in all_os:
        iso_id = f"{os_info.category.value}_{os_info.name.lower()}_{os_info.version.lower()}_{os_info.architecture.value}"

        # Check if there's a database override
        if iso_id in override_map:
            override = override_map[iso_id]
            # Create OSInfo from database override
            from core.models import OSInfo, Architecture as ArchEnum
            merged_os[iso_id] = OSInfo(
                name=override.name,
                version=override.version,
                category=category_enum,
                architecture=ArchEnum(override.architecture.upper()),
                language=override.language,
                url=override.url,
                size=override.size or 0,
                description=override.description,
                icon=override.icon,
                checksum=override.checksum,
                checksum_type=override.checksum_type,
                source="Database Override",
            )
        else:
            merged_os[iso_id] = os_info

    # Also add any custom ISOs that aren't in built-in list
    for override in overrides:
        iso_id = override.iso_id
        if iso_id not in merged_os:
            from core.models import OSInfo, Architecture as ArchEnum
            merged_os[iso_id] = OSInfo(
                name=override.name,
                version=override.version,
                category=category_enum,
                architecture=ArchEnum(override.architecture.upper()),
                language=override.language,
                url=override.url,
                size=override.size or 0,
                description=override.description,
                icon=override.icon,
                checksum=override.checksum,
                checksum_type=override.checksum_type,
                source="Custom",
            )

    # Filter by subcategory if specified
    if subcategory:
        all_os = [os for os in merged_os.values() if (getattr(os, 'subcategory', None) or os.name) == subcategory]
    else:
        all_os = list(merged_os.values())

    # Convert to response models
    response = []
    for os_info in all_os:
        try:
            response.append(
                OSInfoResponse(
                    id=f"{os_info.category.value}_{os_info.name.lower()}_{os_info.version.lower()}_{os_info.architecture.value}",
                    name=os_info.name,
                    version=os_info.version,
                    category=category_enum.value,
                    architecture=os_info.architecture,
                    language=os_info.language,
                    size=os_info.size,
                    size_formatted=getattr(os_info, 'size_formatted', None) or f"{os_info.size / (1024**3):.1f} GB" if os_info.size else "Unknown",
                    source=getattr(os_info, 'source', None),
                    icon=os_info.icon,
                    url=os_info.url,
                    checksum=os_info.checksum,
                    checksum_type=os_info.checksum_type,
                    description=os_info.description,
                    release_date=getattr(os_info, 'release_date', None),
                    subcategory=getattr(os_info, 'subcategory', None),
                )
            )
        except Exception as e:
            print(f"DEBUG: Error converting OSInfo: {e}")
            raise

    return response


@router.get("/{category}/{os_id}", response_model=OSInfoResponse)
async def get_os_details(category: str, os_id: str, db: Session = Depends(get_db)) -> OSInfoResponse:
    """
    Get details for a specific OS.
    Database overrides take precedence over built-in ISOs.

    Args:
        category: OS category
        os_id: OS ID

    Returns:
        OS details
    """
    _init_providers()

    # First check database for this ISO ID
    override = db.query(ISOOverride).filter(
        ISOOverride.iso_id == os_id,
        ISOOverride.is_enabled == True
    ).first()

    if override:
        # Return database override
        from core.models import Architecture as ArchEnum
        return OSInfoResponse(
            id=override.iso_id,
            name=override.name,
            version=override.version,
            category=override.category,
            architecture=ArchEnum(override.architecture.upper()),
            language=override.language,
            url=override.url,
            size=override.size or 0,
            size_formatted=f"{override.size / (1024**3):.1f} GB" if override.size else "Unknown",
            source="Database Override",
            icon=override.icon,
            checksum=override.checksum,
            checksum_type=override.checksum_type,
            description=override.description,
            release_date=None,
            subcategory=None,
        )

    # Get all OS for category
    all_os = await get_os_by_category(category, db=db)

    # Find matching OS
    for os_response in all_os:
        if os_response.id == os_id:
            return os_response

    raise HTTPException(status_code=404, detail="OS not found")


@router.get("/search", response_model=List[OSInfoResponse])
async def search_os(
    query: str,
    category: str | None = None,
    db: Session = Depends(get_db),
) -> List[OSInfoResponse]:
    """
    Search for OS by name or version.
    Includes database overrides and custom ISOs.

    Args:
        query: Search query
        category: Filter by category (optional)

    Returns:
        List of matching OS
    """
    _init_providers()

    registry = get_registry()

    results = {}

    # Parse category if provided
    if category:
        try:
            categories_to_search = [OSCategory(category.lower())]
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category: {category}"
            )
    else:
        categories_to_search = list(OSCategory)

    # Get all database overrides
    all_overrides = db.query(ISOOverride).filter(
        ISOOverride.is_enabled == True
    ).all()

    # Build override map
    override_map = {}
    for override in all_overrides:
        override_map[override.iso_id] = override

    for cat in categories_to_search:
        providers = registry.get_by_category(cat)
        for provider in providers:
            try:
                os_list = await provider.fetch_available()
                for os_info in os_list:
                    iso_id = f"{os_info.category.value}_{os_info.name.lower()}_{os_info.version.lower()}_{os_info.architecture.value}"

                    # Check if there's a database override
                    if iso_id in override_map:
                        override = override_map[iso_id]
                        if (
                            query.lower() in override.name.lower()
                            or query.lower() in override.version.lower()
                        ):
                            if iso_id not in results:
                                from core.models import Architecture as ArchEnum
                                results[iso_id] = OSInfoResponse(
                                    id=override.iso_id,
                                    name=override.name,
                                    version=override.version,
                                    category=override.category,
                                    architecture=ArchEnum(override.architecture.upper()),
                                    language=override.language,
                                    url=override.url,
                                    size=override.size or 0,
                                    size_formatted=f"{override.size / (1024**3):.1f} GB" if override.size else "Unknown",
                                    source="Database Override",
                                    icon=override.icon,
                                    checksum=override.checksum,
                                    checksum_type=override.checksum_type,
                                    description=override.description,
                                    release_date=None,
                                    subcategory=None,
                                )
                    else:
                        # Search in name and version
                        if (
                            query.lower() in os_info.name.lower()
                            or query.lower() in os_info.version.lower()
                        ):
                            if iso_id not in results:
                                results[iso_id] = OSInfoResponse(
                                    id=iso_id,
                                    name=os_info.name,
                                    version=os_info.version,
                                    category=cat.value,
                                    architecture=os_info.architecture,
                                    language=os_info.language,
                                    size=os_info.size,
                                    size_formatted=os_info.size_formatted,
                                    source=os_info.source,
                                    icon=os_info.icon,
                                    url=os_info.url,
                                    checksum=os_info.checksum,
                                    checksum_type=os_info.checksum_type,
                                    description=os_info.description,
                                    release_date=os_info.release_date,
                                    subcategory=os_info.subcategory,
                                )
            except Exception:
                pass

    # Also search in database overrides that might not be in built-in list
    for override in all_overrides:
        if (
            query.lower() in override.name.lower()
            or query.lower() in override.version.lower()
        ):
            if override.iso_id not in results:
                from core.models import Architecture as ArchEnum
                results[override.iso_id] = OSInfoResponse(
                    id=override.iso_id,
                    name=override.name,
                    version=override.version,
                    category=override.category,
                    architecture=ArchEnum(override.architecture.upper()),
                    language=override.language,
                    url=override.url,
                    size=override.size or 0,
                    size_formatted=f"{override.size / (1024**3):.1f} GB" if override.size else "Unknown",
                    source="Database Override",
                    icon=override.icon,
                    checksum=override.checksum,
                    checksum_type=override.checksum_type,
                    description=override.description,
                    release_date=None,
                    subcategory=None,
                )

    return list(results.values())
