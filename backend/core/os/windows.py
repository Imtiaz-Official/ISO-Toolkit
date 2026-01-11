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
            # Windows 11 24H2 - x64 Consumer Edition
            OSInfo(
                name="Windows 11",
                version="24H2",
                category=OSCategory.WINDOWS,
                architecture=Architecture.X64,
                language="en-US",
                url="https://software-static.download.prss.microsoft.com/dbazure/888969d5-f34g-4e03-ac9d-1f9786c66749/26100.3361.250915-1905.24h2_ge_release_svc_refresh_CLIENT_CONSUMER_x64FRE_en-us.iso",
                size=5500000000,
                release_date=datetime(2024, 10, 1),
                description="Windows 11 Version 24H2 - Official Microsoft ISO (Consumer Editions)",
                icon="🪟",
                source="Microsoft (via massgrave.dev)",
                subcategory="Windows 11",
            ),
        ]

        return self._apply_filters(isos, **filters)

    async def _fetch_windows_10(self, **filters) -> List[OSInfo]:
        """
        Fetch Windows 10 ISO information.

        URLs extracted from massgrave.dev using Botasaurus Cloudflare bypass.
        Windows 10 links use buzzheavier.com redirect service.
        """
        isos = [
            # Windows 10 22H2 - x64 Consumer Edition (via buzzheavier.com)
            OSInfo(
                name="Windows 10",
                version="22H2",
                category=OSCategory.WINDOWS,
                architecture=Architecture.X64,
                language="en-US",
                url="https://buzzheavier.com/fuxscqu93mnn",
                size=5800000000,
                release_date=datetime(2024, 10, 17),
                description="Windows 10 Version 22H2 - Consumer Editions (Updated October 2025)",
                icon="🪟",
                source="buzzheavier.com (via massgrave.dev)",
                subcategory="Windows 10",
            ),
            # Windows 10 22H2 - x64 Business Edition (via buzzheavier.com)
            OSInfo(
                name="Windows 10",
                version="22H2 Business",
                category=OSCategory.WINDOWS,
                architecture=Architecture.X64,
                language="en-US",
                url="https://buzzheavier.com/6tglbbetyyav",
                size=4900000000,
                release_date=datetime(2025, 3, 15),
                description="Windows 10 Version 22H2 - Business Editions (Enterprise/Professional/Education) Updated March 2025",
                icon="🪟",
                source="buzzheavier.com (via massgrave.dev)",
                subcategory="Windows 10",
            ),
        ]

        return self._apply_filters(isos, **filters)

    async def _fetch_windows_81(self, **filters) -> List[OSInfo]:
        """
        Fetch Windows 8.1 ISO information from Internet Archive.
        """
        isos = [
            OSInfo(
                name="Windows 8.1",
                version="Professional",
                category=OSCategory.WINDOWS,
                architecture=Architecture.X64,
                language="en-US",
                url="https://archive.org/download/win81pro_x64/en-us_windows_8.1_professional_x64.iso",
                size=3909742592,
                release_date=datetime(2014, 2, 27),
                description="Windows 8.1 Professional x64",
                icon="🪟",
                source="Internet Archive",
                subcategory="Windows 8.1",
            ),
            OSInfo(
                name="Windows 8.1",
                version="Professional",
                category=OSCategory.WINDOWS,
                architecture=Architecture.X86,
                language="en-US",
                url="https://archive.org/download/win81pro_x86/en-us_windows_8.1_professional_x86.iso",
                size=3019898880,
                release_date=datetime(2014, 2, 27),
                description="Windows 8.1 Professional x86",
                icon="🪟",
                source="Internet Archive",
                subcategory="Windows 8.1",
            ),
        ]

        return self._apply_filters(isos, **filters)

    async def _fetch_windows_7(self, **filters) -> List[OSInfo]:
        """
        Fetch Windows 7 ISO information from Internet Archive.
        """
        isos = [
            OSInfo(
                name="Windows 7",
                version="Professional SP1",
                category=OSCategory.WINDOWS,
                architecture=Architecture.X64,
                language="en-US",
                url="https://archive.org/download/win7pro_x64_sp1/en_windows_7_professional_with_sp1_x64_dvd_u_677056.iso",
                size=3265291264,
                release_date=datetime(2011, 2, 22),
                description="Windows 7 Professional SP1 x64",
                icon="🪟",
                source="Internet Archive",
                subcategory="Windows 7",
            ),
            OSInfo(
                name="Windows 7",
                version="Ultimate SP1",
                category=OSCategory.WINDOWS,
                architecture=Architecture.X64,
                language="en-US",
                url="https://archive.org/download/win7ult_x64_sp1/en_windows_7_ultimate_with_sp1_x64_dvd_u_677332.iso",
                size=3386296320,
                release_date=datetime(2011, 2, 22),
                description="Windows 7 Ultimate SP1 x64",
                icon="🪟",
                source="Internet Archive",
                subcategory="Windows 7",
            ),
            OSInfo(
                name="Windows 7",
                version="Professional SP1",
                category=OSCategory.WINDOWS,
                architecture=Architecture.X86,
                language="en-US",
                url="https://archive.org/download/win7pro_x86_sp1/en_windows_7_professional_with_sp1_x86_dvd_u_676951.iso",
                size=2465423360,
                release_date=datetime(2011, 2, 22),
                description="Windows 7 Professional SP1 x86",
                icon="🪟",
                source="Internet Archive",
                subcategory="Windows 7",
            ),
        ]

        return self._apply_filters(isos, **filters)

    async def _fetch_windows_xp(self, **filters) -> List[OSInfo]:
        """
        Fetch Windows XP ISO information from Internet Archive.
        """
        isos = [
            OSInfo(
                name="Windows XP",
                version="Professional SP3",
                category=OSCategory.WINDOWS,
                architecture=Architecture.X86,
                language="en-US",
                url="https://archive.org/download/winxppro_sp3/xp_professional_with_service_pack_3_x86_cd_x14-79513.iso",
                size=618459136,
                release_date=datetime(2008, 4, 21),
                description="Windows XP Professional SP3",
                icon="🪟",
                source="Internet Archive",
                subcategory="Windows XP",
            ),
            OSInfo(
                name="Windows XP",
                version="Home SP3",
                category=OSCategory.WINDOWS,
                architecture=Architecture.X86,
                language="en-US",
                url="https://archive.org/download/winxphome_sp3/xp_home_with_service_pack_3_x86_cd_x14-79513.iso",
                size=630194176,
                release_date=datetime(2008, 4, 21),
                description="Windows XP Home SP3",
                icon="🪟",
                source="Internet Archive",
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
