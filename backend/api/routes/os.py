"""
API routes for OS listings and browsing.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Union
import asyncio

from api.models.schemas import (
    OSInfoResponse,
    OSCategoryResponse,
    LinuxSubcategoryResponse,
    Architecture,
)
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


@router.get("/{category}", response_model=List[OSInfoResponse])
async def get_os_by_category(
    category: str,
    architecture: Architecture | None = None,
    language: str | None = None,
    subcategory: str | None = None,
) -> List[OSInfoResponse]:
    """
    Get available OS for a specific category.

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
        category = OSCategory(category.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category: {category}. Valid options: windows, linux, macos, bsd"
        )

    registry = get_registry()
    providers = registry.get_by_category(category)
    print(f"DEBUG: Category={category}, Providers found={len(providers)}")

    all_os = []
    for provider in providers:
        try:
            print(f"DEBUG: Calling fetch_available on provider with filters: architecture={architecture}, language={language}")
            os_list = await provider.fetch_available(
                architecture=architecture,
                language=language,
            )
            print(f"DEBUG: Provider returned {len(os_list)} ISOs")
            all_os.extend(os_list)
        except Exception as e:
            print(f"DEBUG: Exception from provider: {e}")
            raise HTTPException(status_code=500, detail=f"Error fetching OS: {str(e)}")

    # Filter by subcategory if specified
    if subcategory:
        all_os = [os for os in all_os if (os.subcategory or os.name) == subcategory]

    # Convert to response models
    print(f"DEBUG: Converting {len(all_os)} OSInfo objects to response")
    response = []
    for os_info in all_os:
        try:
            response.append(
                OSInfoResponse(
                    id=f"{os_info.category.value}_{os_info.name.lower()}_{os_info.version.lower()}_{os_info.architecture.value}",
                    name=os_info.name,
                    version=os_info.version,
                    category=category.value,  # Use string value, not enum
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
            )
        except Exception as e:
            print(f"DEBUG: Error converting OSInfo: {e}")
            raise

    print(f"DEBUG: Returning {len(response)} items")
    return response


@router.get("/{category}/{os_id}", response_model=OSInfoResponse)
async def get_os_details(category: str, os_id: str) -> OSInfoResponse:
    """
    Get details for a specific OS.

    Args:
        category: OS category
        os_id: OS ID

    Returns:
        OS details
    """
    _init_providers()

    # Get all OS for category
    all_os = await get_os_by_category(category)

    # Find matching OS
    for os_response in all_os:
        if os_response.id == os_id:
            return os_response

    raise HTTPException(status_code=404, detail="OS not found")


@router.get("/search", response_model=List[OSInfoResponse])
async def search_os(
    query: str,
    category: str | None = None,
) -> List[OSInfoResponse]:
    """
    Search for OS by name or version.

    Args:
        query: Search query
        category: Filter by category (optional)

    Returns:
        List of matching OS
    """
    _init_providers()

    registry = get_registry()

    results = []

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

    for cat in categories_to_search:
        providers = registry.get_by_category(cat)
        for provider in providers:
            try:
                os_list = await provider.fetch_available()
                for os_info in os_list:
                    # Search in name and version
                    if (
                        query.lower() in os_info.name.lower()
                        or query.lower() in os_info.version.lower()
                    ):
                        results.append(
                            OSInfoResponse(
                                id=f"{os_info.category.value}_{os_info.name.lower()}_{os_info.version.lower()}_{os_info.architecture.value}",
                                name=os_info.name,
                                version=os_info.version,
                                category=cat.value,  # Use string value
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
                        )
            except Exception:
                pass

    return results
