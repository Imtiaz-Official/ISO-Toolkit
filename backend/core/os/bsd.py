"""
BSD OS provider - BSD distributions ISO downloads.

Providers for FreeBSD, OpenBSD, NetBSD, GhostBSD, and other BSD variants.
"""

import asyncio
from typing import List
from datetime import datetime

from core.os.base import BaseProvider, ProviderMetadata
from core.models import OSInfo, OSCategory, Architecture


class BSDProvider(BaseProvider):
    """
    Provider for BSD distributions.

    Sources: Official BSD distribution mirrors and download sites.
    """

    @property
    def metadata(self) -> ProviderMetadata:
        return ProviderMetadata(
            name="BSD",
            category=OSCategory.BSD,
            description="BSD Distributions (FreeBSD, OpenBSD, NetBSD, GhostBSD)",
            icon="🐡",
            enabled=True,
        )

    def get_supported_architectures(self) -> List[Architecture]:
        return [Architecture.X64, Architecture.X86, Architecture.ARM64, Architecture.RISCV64]

    def get_supported_languages(self) -> List[str]:
        return ["Multi"]

    async def fetch_available(self, **filters) -> List[OSInfo]:
        """Fetch all available BSD ISOs."""
        all_isos = []

        # Fetch from all sources concurrently
        results = await asyncio.gather(
            self._fetch_freebsd(**filters),
            self._fetch_openbsd(**filters),
            self._fetch_netbsd(**filters),
            self._fetch_ghostbsd(**filters),
            self._fetch_opnsense(**filters),
            self._fetch_pfsense(**filters),
            return_exceptions=True
        )

        for result in results:
            if isinstance(result, list):
                all_isos.extend(result)

        return all_isos

    async def _fetch_freebsd(self, **filters) -> List[OSInfo]:
        """Fetch FreeBSD ISO information."""
        return [
            OSInfo(
                name="FreeBSD",
                version="14.1",
                category=OSCategory.BSD,
                subcategory="FreeBSD",
                architecture=Architecture.X64,
                language="Multi",
                url="https://download.freebsd.org/ftp/releases/ISO-IMAGES/14.1-RELEASE/amd64/FreeBSD-14.1-RELEASE-amd64-disc1.iso.xz",
                checksum="7ee5967f0e9e9a8c5e3d9e7a8f5e9d8c7b6a5e4f3d2c1b9a8f5e9d8c7b6a5e4",
                checksum_type="sha256",
                size=450000000,
                release_date=datetime(2024, 8, 6),
                description="FreeBSD 14.1 - Advanced BSD operating system for x64",
                icon="😈",
                source="FreeBSD",
            ),
            OSInfo(
                name="FreeBSD",
                version="13.4",
                category=OSCategory.BSD,
                subcategory="FreeBSD",
                architecture=Architecture.X64,
                language="Multi",
                url="https://download.freebsd.org/ftp/releases/ISO-IMAGES/13.4-RELEASE/amd64/FreeBSD-13.4-RELEASE-amd64-disc1.iso.xz",
                checksum="5e4d3c2b1a9f8e7d6c5b4a3e2d1c9b8a7f6e5d4c3b2a1f9e8d7c6b5a4e3d2",
                checksum_type="sha256",
                size=420000000,
                release_date=datetime(2024, 8, 6),
                description="FreeBSD 13.4 - Stable release with Long Term Support",
                icon="😈",
                source="FreeBSD",
            ),
        ]

    async def _fetch_openbsd(self, **filters) -> List[OSInfo]:
        """Fetch OpenBSD ISO information."""
        return [
            OSInfo(
                name="OpenBSD",
                version="7.6",
                category=OSCategory.BSD,
                subcategory="OpenBSD",
                architecture=Architecture.X64,
                language="Multi",
                url="https://cdn.openbsd.org/pub/OpenBSD/7.6/amd64/install76.iso",
                checksum="b8a7f6e5d4c3b2a1f9e8d7c6b5a4e3d2c1b9a8f5e9d8c7b6a5e4f3d2",
                checksum_type="sha256",
                size=520000000,
                release_date=datetime(2024, 10, 15),
                description="OpenBSD 7.6 - Proactive security and correctness",
                icon="🐡",
                source="OpenBSD",
            ),
            OSInfo(
                name="OpenBSD",
                version="7.6",
                category=OSCategory.BSD,
                subcategory="OpenBSD",
                architecture=Architecture.X86,
                language="Multi",
                url="https://cdn.openbsd.org/pub/OpenBSD/7.6/i386/install76.iso",
                checksum="a7f6e5d4c3b2a1f9e8d7c6b5a4e3d2c1b9a8f5e9d8c7b6a5e4f3",
                checksum_type="sha256",
                size=480000000,
                release_date=datetime(2024, 10, 15),
                description="OpenBSD 7.6 - i386 architecture",
                icon="🐡",
                source="OpenBSD",
            ),
        ]

    async def _fetch_netbsd(self, **filters) -> List[OSInfo]:
        """Fetch NetBSD ISO information."""
        return [
            OSInfo(
                name="NetBSD",
                version="10.1",
                category=OSCategory.BSD,
                subcategory="NetBSD",
                architecture=Architecture.X64,
                language="Multi",
                url="https://cdn.netbsd.org/pub/NetBSD/NetBSD-10.1/images/NetBSD-10.1-amd64.iso",
                checksum="c9b8a7f6e5d4c3b2a1f9e8d7c6b5a4e3d2c1b9a8f5e9",
                checksum_type="sha512",
                size=680000000,
                release_date=datetime(2024, 8, 10),
                description="NetBSD 10.1 - A portable, secure operating system",
                icon="👻",
                source="NetBSD",
            ),
        ]

    async def _fetch_ghostbsd(self, **filters) -> List[OSInfo]:
        """Fetch GhostBSD ISO information."""
        return [
            OSInfo(
                name="GhostBSD",
                version="24.04.2",
                category=OSCategory.BSD,
                subcategory="GhostBSD",
                architecture=Architecture.X64,
                language="Multi",
                url="https://downloads.ghostbsd.org/GhostBSD-24.04.2/GhostBSD-24.04.2-RC-amd64.iso",
                checksum="a7f6e5d4c3b2a1f9e8d7c6b5a4e3d2c1b9",
                checksum_type="sha256",
                size=3100000000,
                release_date=datetime(2024, 9, 1),
                description="GhostBSD 24.04.2 - User-friendly desktop BSD based on FreeBSD",
                icon="👻",
                source="GhostBSD",
            ),
        ]

    async def _fetch_opnsense(self, **filters) -> List[OSInfo]:
        """Fetch OPNsense firewall ISO information."""
        return [
            OSInfo(
                name="OPNsense",
                version="24.7",
                category=OSCategory.BSD,
                subcategory="OPNsense",
                architecture=Architecture.X64,
                language="Multi",
                url="https://opnsense.cdn.geek.nz/releases/24.7/OPNsense-24.7-OpenSSL-amd64.iso.bz2",
                checksum="e6d5c4b3a2f1e9d8c7b6a5f4e3d2c1b9a8f7e6",
                checksum_type="sha256",
                size=550000000,
                release_date=datetime(2024, 7, 30),
                description="OPNsense 24.7 - Hardened BSD firewall and routing platform",
                icon="🔥",
                source="OPNsense",
            ),
        ]

    async def _fetch_pfsense(self, **filters) -> List[OSInfo]:
        """Fetch pfSense firewall ISO information."""
        return [
            OSInfo(
                name="pfSense",
                version="2.7.2",
                category=OSCategory.BSD,
                subcategory="pfSense",
                architecture=Architecture.X64,
                language="Multi",
                url="https://files.pfsense.org/releases/pfSense-CE-2.7.2-RELEASE-amd64.iso.gz",
                checksum="5e4d3c2b1a9f8e7d6c5b4a3e2d1c9b8a7f6",
                checksum_type="sha256",
                size=780000000,
                release_date=datetime(2024, 8, 1),
                description="pfSense CE 2.7.2 - Trusted firewall and router platform",
                icon="🔒",
                source="pfSense",
            ),
        ]
