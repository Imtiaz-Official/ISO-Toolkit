"""
Windows OS provider - scrapers for Windows ISO downloads.

Updated with working URLs and proper headers for 2025.
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
    - Windows 11/10: Official Microsoft downloads via massgrave.dev
    - Older Windows: Internet Archive and software archives
    """

    @property
    def metadata(self) -> ProviderMetadata:
        return ProviderMetadata(
            name="Windows",
            category=OSCategory.WINDOWS,
            description="Microsoft Windows (XP, 7, 8.1, 10, 11)",
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
        Fetch Windows 11 ISO information.

        Uses massgrave.dev with proper headers - these redirect to official Microsoft downloads.
        """
        # Common headers for massgrave.dev
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
        }

        isos = [
            # Windows 11 24H2 (latest) - x64
            OSInfo(
                name="Windows 11",
                version="24H2",
                category=OSCategory.WINDOWS,
                architecture=Architecture.X64,
                language="en-US",
                url="https://drive.massgrave.dev/en-us_windows_11_consumer_editions_version_24h2_x64_dvd_4cc8f7e9.iso",
                mirrors=[
                    "https://iso.massgrave.dev/en-us_windows_11_consumer_editions_version_24h2_x64_dvd_4cc8f7e9.iso",
                ],
                size=5434012160,
                release_date=datetime(2024, 11, 12),
                description="Windows 11 Version 24H2 - Official Microsoft ISO",
                icon="🪟",
                source="Microsoft (massgrave.dev)",
                headers=headers,
            ),
            # Windows 11 23H2 - x64
            OSInfo(
                name="Windows 11",
                version="23H2",
                category=OSCategory.WINDOWS,
                architecture=Architecture.X64,
                language="en-US",
                url="https://drive.massgrave.dev/en-us_windows_11_consumer_editions_version_23h2_x64_dvd_d470d1f8.iso",
                mirrors=[
                    "https://iso.massgrave.dev/en-us_windows_11_consumer_editions_version_23h2_x64_dvd_d470d1f8.iso",
                ],
                size=5140709376,
                release_date=datetime(2024, 9, 17),
                description="Windows 11 Version 23H2 - Official Microsoft ISO",
                icon="🪟",
                source="Microsoft (massgrave.dev)",
                headers=headers,
            ),
        ]

        return self._apply_filters(isos, **filters)

    async def _fetch_windows_10(self, **filters) -> List[OSInfo]:
        """
        Fetch Windows 10 ISO information.

        Uses massgrave.dev with proper headers - these redirect to official Microsoft downloads.
        """
        # Common headers for massgrave.dev
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
        }

        isos = [
            OSInfo(
                name="Windows 10",
                version="22H2",
                category=OSCategory.WINDOWS,
                architecture=Architecture.X64,
                language="en-US",
                url="https://drive.massgrave.dev/en-us_windows_10_consumer_editions_version_22h2_x64_dvd_3f50b8b6.iso",
                mirrors=[
                    "https://iso.massgrave.dev/en-us_windows_10_consumer_editions_version_22h2_x64_dvd_3f50b8b6.iso",
                ],
                size=5850961920,
                release_date=datetime(2024, 10, 17),
                description="Windows 10 Version 22H2 - Official Microsoft ISO",
                icon="🪟",
                source="Microsoft (massgrave.dev)",
                headers=headers,
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
