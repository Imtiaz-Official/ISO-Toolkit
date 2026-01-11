"""
Windows OS provider - scrapers for Windows ISO downloads.

ISO URLs extracted using Botasaurus Cloudflare bypass from massgrave.dev.
"""

import asyncio
from typing import List
from datetime import datetime

from core.os.base import BaseProvider, ProviderMetadata
from core.models import OSInfo, OSCategory, Architecture


class WindowsProvider(BaseProvider):
    """
    Provider for Windows ISO downloads.

    Sources:
    - Windows 11/10: Official Microsoft CDN (via massgrave.dev)
    - Older Windows: Internet Archive

    URLs extracted using Botasaurus: https://github.com/omkarcloud/botasaurus
    """

    @property
    def metadata(self) -> ProviderMetadata:
        return ProviderMetadata(
            name="Windows",
            category=OSCategory.WINDOWS,
            description="Microsoft Windows (XP, 7, 8.1, 10, 11) - Latest versions from Microsoft",
            icon="🪟",
            enabled=True,
        )

    def get_supported_architectures(self) -> List[Architecture]:
        return [Architecture.X64, Architecture.X86, Architecture.ARM64]

    def get_supported_languages(self) -> List[str]:
        return ["en-US"]

    async def fetch_available(self, **filters) -> List[OSInfo]:
        """Fetch all available Windows ISOs."""
        all_isos = []

        # Fetch from all sources concurrently
        results = await asyncio.gather(
            self._fetch_windows_11(**filters),
            self._fetch_windows_10(**filters),
            self._fetch_windows_81(**filters),
            self._fetch_windows_7(**filters),
            self._fetch_windows_xp(**filters),
            return_exceptions=True
        )

        for result in results:
            if isinstance(result, list):
                all_isos.extend(result)

        return all_isos

    async def _fetch_windows_11(self, **filters) -> List[OSInfo]:
        """
        Fetch Windows 11 ISO information from Microsoft CDN.

        URLs extracted from massgrave.dev using Botasaurus Cloudflare bypass.
        """
        isos = [
            # Windows 11 25H2 (latest) - x64 Consumer Edition
            OSInfo(
                name="Windows 11",
                version="25H2",
                category=OSCategory.WINDOWS,
                architecture=Architecture.X64,
                language="en-US",
                url="https://software-static.download.prss.microsoft.com/dbazure/888969d5-f34g-4e03-ac9d-1f9786c66749/26200.6584.250915-1905.25h2_ge_release_svc_refresh_CLIENT_CONSUMER_x64FRE_en-us.iso",
                size=7740000000,
                release_date=datetime(2024, 12, 1),
                description="Windows 11 Version 25H2 - Official Microsoft ISO (Consumer Editions)",
                icon="🪟",
                source="Microsoft (via massgrave.dev)",
                subcategory="Windows 11",
            ),
            # Windows 11 24H2 - URL expired (403 Forbidden from dl.os.click)
            # TODO: Find working mirror for Windows 11 24H2
        ]

        return self._apply_filters(isos, **filters)

    async def _fetch_windows_10(self, **filters) -> List[OSInfo]:
        """
        Fetch Windows 10 ISO information from TrashBytes mirror.
        Build 19045.6456 (October 2025) - Final Windows 10 release.
        """
        isos = [
            # Windows 10 22H2 - x64 Consumer Edition
            OSInfo(
                name="Windows 10",
                version="22H2",
                category=OSCategory.WINDOWS,
                architecture=Architecture.X64,
                language="en-US",
                url="https://trashbytes.net/dl/ako3j7Xa4laRBeh9yB8VBQuWm1aXVxeZi1-BN3PCWNrksJ1ZkGNGUWyH9Is68vpNY3gRgsJK0kZrynM_L0_1OvsoDkhvAog2_-3enPE2t8yn-ehb7zdYUFwKF2iaifUoaonQxv883ucirHVr2UXO38QCJvOEVx9_tdlD5W0zzY1uFPtal_WU12AYp8GfrQss4VcKiCuDk_C9",
                size=5800000000,
                release_date=datetime(2024, 10, 17),
                description="Windows 10 Version 22H2 - Consumer Editions (Updated October 2025, Build 19045.6456)",
                icon="🪟",
                source="TrashBytes",
                subcategory="Windows 10",
            ),
        ]

        return self._apply_filters(isos, **filters)

    async def _fetch_windows_81(self, **filters) -> List[OSInfo]:
        """
        Fetch Windows 8.1 ISO information - currently unavailable.

        Archive.org is experiencing service issues (503 errors).
        TODO: Find working mirror for Windows 8.1 ISOs.
        """
        isos = []
        return self._apply_filters(isos, **filters)

    async def _fetch_windows_7(self, **filters) -> List[OSInfo]:
        """
        Fetch Windows 7 ISO information from archive.isdn.network mirror.
        """
        isos = [
            # Windows 7 Ultimate SP1 x64 - Working URL
            OSInfo(
                name="Windows 7",
                version="Ultimate SP1",
                category=OSCategory.WINDOWS,
                architecture=Architecture.X64,
                language="en-US",
                url="https://archive.isdn.network/windows/en_windows_7_ultimate_with_sp1_x64_dvd_u_677332.iso",
                size=3386296320,
                release_date=datetime(2011, 2, 22),
                description="Windows 7 Ultimate SP1 x64",
                icon="🪟",
                source="archive.isdn.network",
                subcategory="Windows 7",
            ),
        ]

        return self._apply_filters(isos, **filters)

    async def _fetch_windows_xp(self, **filters) -> List[OSInfo]:
        """
        Fetch Windows XP ISO information from archive.isdn.network mirror.
        """
        isos = [
            OSInfo(
                name="Windows XP",
                version="Professional SP3",
                category=OSCategory.WINDOWS,
                architecture=Architecture.X86,
                language="en-US",
                url="https://archive.isdn.network/windows/en_windows_xp_professional_with_service_pack_3_x86_cd_vl_x14-73974.iso",
                size=618459136,
                release_date=datetime(2008, 4, 21),
                description="Windows XP Professional SP3 VL (Volume License)",
                icon="🪟",
                source="archive.isdn.network",
                subcategory="Windows XP",
            ),
            OSInfo(
                name="Windows XP",
                version="Home SP3",
                category=OSCategory.WINDOWS,
                architecture=Architecture.X86,
                language="en-US",
                url="https://archive.isdn.network/windows/xp_home_with_service_pack_3_x86_cd_x14-79513.iso",
                size=630194176,
                release_date=datetime(2008, 4, 21),
                description="Windows XP Home SP3",
                icon="🪟",
                source="archive.isdn.network",
                subcategory="Windows XP",
            ),
        ]

        return self._apply_filters(isos, **filters)

    def _apply_filters(self, isos: List[OSInfo], **filters) -> List[OSInfo]:
        """Apply filters to a list of OSInfo objects."""
        filtered = isos

        if "architecture" in filters and filters["architecture"] is not None:
            filtered = [iso for iso in filtered if iso.architecture == filters["architecture"]]

        if "language" in filters and filters["language"] is not None:
            filtered = [iso for iso in filtered if iso.language == filters["language"]]

        if "version" in filters and filters["version"] is not None:
            filtered = [iso for iso in filtered if filters["version"] in iso.version]

        return filtered
