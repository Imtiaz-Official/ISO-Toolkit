"""
macOS OS provider - macOS ISO downloads.

Note: macOS downloads are sourced from Internet Archive and other archives
since official Apple downloads require Apple ID authentication.
"""

import asyncio
from typing import List
from datetime import datetime

from core.os.base import BaseProvider, ProviderMetadata
from core.models import OSInfo, OSCategory, Architecture


class MacOSProvider(BaseProvider):
    """
    Provider for macOS ISO/downloads.

    Sources: Internet Archive and other archives for macOS installers.
    """

    @property
    def metadata(self) -> ProviderMetadata:
        return ProviderMetadata(
            name="macOS",
            category=OSCategory.MACOS,
            description="Apple macOS (Monterey, Ventura, Sonoma, Sequoia)",
            icon="🍎",
            enabled=True,
        )

    def get_supported_architectures(self) -> List[Architecture]:
        return [Architecture.X64, Architecture.ARM64]

    def get_supported_languages(self) -> List[str]:
        return ["Multi"]

    async def fetch_available(self, **filters) -> List[OSInfo]:
        """Fetch all available macOS ISOs."""
        all_isos = []

        # Fetch from all sources concurrently
        results = await asyncio.gather(
            self._fetch_macos_sequoia(**filters),
            self._fetch_macos_sonoma(**filters),
            self._fetch_macos_ventura(**filters),
            self._fetch_macos_monterey(**filters),
            self._fetch_macos_big_sur(**filters),
            self._fetch_macos_catalina(**filters),
            self._fetch_macos_mojave(**filters),
            return_exceptions=True
        )

        for result in results:
            if isinstance(result, list):
                all_isos.extend(result)

        return all_isos

    async def _fetch_macos_sequoia(self, **filters) -> List[OSInfo]:
        """Fetch macOS Sequoia (15.x) ISO information."""
        return [
            OSInfo(
                name="macOS Sequoia",
                version="15.1",
                category=OSCategory.MACOS,
                architecture=Architecture.ARM64,
                language="Multi",
                url="https://archive.org/download/macos-sequoia-15.1/Install macOS Sequoia 15.1.ipsw",
                checksum="",
                checksum_type="",
                size=14500000000,
                release_date=datetime(2024, 10, 25),
                description="macOS Sequoia 15.1 - Apple Silicon",
                icon="🍎",
                source="Internet Archive",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                },
            ),
        ]

    async def _fetch_macos_sonoma(self, **filters) -> List[OSInfo]:
        """Fetch macOS Sonoma (14.x) ISO information - disabled due to Archive.org issues."""
        # Archive.org is returning 503 Service Unavailable for macOS ISOs
        # Apple requires developer account for direct downloads
        # TODO: Find alternative mirror or use Apple's developer tools
        return []

    async def _fetch_macos_ventura(self, **filters) -> List[OSInfo]:
        """Fetch macOS Ventura (13.x) ISO information."""
        return [
            OSInfo(
                name="macOS Ventura",
                version="13.7.1",
                category=OSCategory.MACOS,
                architecture=Architecture.X64,
                language="Multi",
                url="https://archive.org/download/macos-ventura-13.7.1/Install macOS Ventura 13.7.1.iso",
                checksum="",
                checksum_type="",
                size=12800000000,
                release_date=datetime(2024, 10, 25),
                description="macOS Ventura 13.7.1 - Intel",
                icon="🍎",
                source="Internet Archive",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                },
            ),
        ]

    async def _fetch_macos_monterey(self, **filters) -> List[OSInfo]:
        """Fetch macOS Monterey (12.x) ISO information."""
        return [
            OSInfo(
                name="macOS Monterey",
                version="12.7.6",
                category=OSCategory.MACOS,
                architecture=Architecture.X64,
                language="Multi",
                url="https://archive.org/download/macos-monterey-12.7.6/Install macOS Monterey 12.7.6.iso",
                checksum="",
                checksum_type="",
                size=16200000000,
                release_date=datetime(2024, 10, 25),
                description="macOS Monterey 12.7.6 - Intel",
                icon="🍎",
                source="Internet Archive",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                },
            ),
        ]

    async def _fetch_macos_big_sur(self, **filters) -> List[OSInfo]:
        """Fetch macOS Big Sur (11.x) ISO information."""
        return [
            OSInfo(
                name="macOS Big Sur",
                version="11.7.10",
                category=OSCategory.MACOS,
                architecture=Architecture.X64,
                language="Multi",
                url="https://archive.org/download/macos-big-sur-11.7.10/Install macOS Big Sur 11.7.10.iso",
                checksum="",
                checksum_type="",
                size=16500000000,
                release_date=datetime(2024, 10, 25),
                description="macOS Big Sur 11.7.10 - Intel",
                icon="🍎",
                source="Internet Archive",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                },
            ),
        ]

    async def _fetch_macos_catalina(self, **filters) -> List[OSInfo]:
        """Fetch macOS Catalina (10.15.x) ISO information."""
        return [
            OSInfo(
                name="macOS Catalina",
                version="10.15.7",
                category=OSCategory.MACOS,
                architecture=Architecture.X64,
                language="Multi",
                url="https://archive.org/download/macos-catalina-10.15.7/Install macOS Catalina 10.15.7.iso",
                checksum="",
                checksum_type="",
                size=8800000000,
                release_date=datetime(2024, 10, 25),
                description="macOS Catalina 10.15.7 - Intel",
                icon="🍎",
                source="Internet Archive",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                },
            ),
        ]

    async def _fetch_macos_mojave(self, **filters) -> List[OSInfo]:
        """Fetch macOS Mojave (10.14.x) ISO information."""
        return [
            OSInfo(
                name="macOS Mojave",
                version="10.14.6",
                category=OSCategory.MACOS,
                architecture=Architecture.X64,
                language="Multi",
                url="https://archive.org/download/macos-mojave-10.14.6/Install macOS Mojave 10.14.6.iso",
                checksum="",
                checksum_type="",
                size=6600000000,
                release_date=datetime(2024, 10, 25),
                description="macOS Mojave 10.14.6 - Intel",
                icon="🍎",
                source="Internet Archive",
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                },
            ),
        ]
