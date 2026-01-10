"""
Linux OS provider - scrapers for Linux distribution ISO downloads.
"""

import asyncio
from typing import List, Optional
from datetime import datetime

from iso_toolkit.os.base import BaseProvider, ProviderMetadata
from iso_toolkit.models import OSInfo, OSCategory, Architecture


class LinuxProvider(BaseProvider):
    """
    Provider for Linux distribution ISO downloads.

    Supports:
    - Ubuntu (Desktop, Server, LTS versions)
    - Fedora
    - Debian
    - Linux Mint
    - Arch Linux
    - openSUSE
    - More distros can be added
    """

    @property
    def metadata(self) -> ProviderMetadata:
        return ProviderMetadata(
            name="Linux",
            category=OSCategory.LINUX,
            description="Linux Distributions (Ubuntu, Fedora, Debian, Mint, Arch, etc.)",
            icon="🐧",
            enabled=True,
        )

    def get_supported_architectures(self) -> List[Architecture]:
        return [Architecture.X64, Architecture.X86, Architecture.ARM64, Architecture.ARM, Architecture.RISCV64]

    def get_supported_languages(self) -> List[str]:
        # Most Linux ISOs are multi-language
        return ["Multi", "en-US", "en-GB"]

    async def fetch_available(self, **filters) -> List[OSInfo]:
        """Fetch all available Linux distribution ISOs."""
        all_isos = []

        # Fetch from all distros concurrently
        results = await asyncio.gather(
            self._fetch_ubuntu(**filters),
            self._fetch_fedora(**filters),
            self._fetch_debian(**filters),
            self._fetch_linux_mint(**filters),
            self._fetch_arch_linux(**filters),
            self._fetch_opensuse(**filters),
            return_exceptions=True
        )

        for result in results:
            if isinstance(result, list):
                all_isos.extend(result)

        return all_isos

    async def _fetch_ubuntu(self, **filters) -> List[OSInfo]:
        """Fetch Ubuntu ISO information."""
        isos = [
            # Ubuntu Desktop LTS
            OSInfo(
                name="Ubuntu Desktop",
                version="24.04 LTS",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://releases.ubuntu.com/24.04/ubuntu-24.04.3-desktop-amd64.iso",
                checksum="e240978654eb5e15b11656cc311a81760b38243b96f59778b80a5d7fc175e070",
                checksum_type="sha256",
                size=5888911360,
                release_date=datetime(2024, 8, 15),
                description="Ubuntu 24.04 LTS Noble Numbat - Long Term Support",
                icon="🟠",
                source="Ubuntu",
            ),
            OSInfo(
                name="Ubuntu Desktop",
                version="22.04 LTS",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://releases.ubuntu.com/22.04/ubuntu-22.04.4-desktop-amd64.iso",
                checksum="c0499d9d1cbe3f41353a9d8c38044928155e03668dcef029a2d4f4e48e49c5e5",
                checksum_type="sha256",
                size=5653567488,
                release_date=datetime(2024, 2, 23),
                description="Ubuntu 22.04 LTS Jammy Jellyfish - Long Term Support",
                icon="🟠",
                source="Ubuntu",
            ),
            OSInfo(
                name="Ubuntu Desktop",
                version="24.04 LTS",
                category=OSCategory.LINUX,
                architecture=Architecture.ARM64,
                language="Multi",
                url="https://cdimage.ubuntu.com/releases/24.04/release/ubuntu-24.04.3-live-server-arm64.iso",
                size=5652480000,
                release_date=datetime(2024, 8, 15),
                description="Ubuntu 24.04 LTS ARM64 - For Raspberry Pi and ARM devices",
                icon="🟠",
                source="Ubuntu",
            ),
            # Ubuntu Server
            OSInfo(
                name="Ubuntu Server",
                version="24.04 LTS",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://releases.ubuntu.com/24.04/ubuntu-24.04.3-live-server-amd64.iso",
                checksum="85049f2d4aa9e5f649a48b89ac49d99a78f72cc3e6e9f2db4df9ec6443c7b3f3",
                checksum_type="sha256",
                size=4044802560,
                release_date=datetime(2024, 8, 15),
                description="Ubuntu 24.04 LTS Server - Optimized for servers",
                icon="🟠",
                source="Ubuntu",
            ),
        ]

        return self._apply_filters(isos, **filters)

    async def _fetch_fedora(self, **filters) -> List[OSInfo]:
        """Fetch Fedora ISO information."""
        isos = [
            OSInfo(
                name="Fedora Workstation",
                version="41",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://download.fedoraproject.org/pub/fedora/linux/releases/41/Workstation/x86_64/iso/Fedora-Workstation-Live-x86_64-41-1.4.iso",
                size=2361398272,
                release_date=datetime(2024, 10, 29),
                description="Fedora 41 Workstation - Latest GNOME desktop",
                icon="🔵",
                source="Fedora Project",
            ),
            OSInfo(
                name="Fedora Server",
                version="41",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://download.fedoraproject.org/pub/fedora/linux/releases/41/Server/x86_64/iso/Fedora-Server-dvd-x86_64-41-1.4.iso",
                size=2684354560,
                release_date=datetime(2024, 10, 29),
                description="Fedora 41 Server - Data center edition",
                icon="🔵",
                source="Fedora Project",
            ),
        ]

        return self._apply_filters(isos, **filters)

    async def _fetch_debian(self, **filters) -> List[OSInfo]:
        """Fetch Debian ISO information."""
        isos = [
            OSInfo(
                name="Debian",
                version="12.8 Bookworm",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-12.8.0-amd64-netinst.iso",
                size=419430400,
                release_date=datetime(2024, 11, 9),
                description="Debian 12.8 Bookworm - Network install",
                icon="🔴",
                source="Debian",
            ),
            OSInfo(
                name="Debian",
                version="12.8 Bookworm",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://cdimage.debian.org/debian-cd/current/amd64/iso-dvd/debian-12.8.0-amd64-DVD-1.iso",
                size=4194304000,
                release_date=datetime(2024, 11, 9),
                description="Debian 12.8 Bookworm - Full DVD",
                icon="🔴",
                source="Debian",
            ),
        ]

        return self._apply_filters(isos, **filters)

    async def _fetch_linux_mint(self, **filters) -> List[OSInfo]:
        """Fetch Linux Mint ISO information."""
        isos = [
            OSInfo(
                name="Linux Mint",
                version="22 \"Wilma\"",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://linuxmint.com/iso/stable/linuxmint-22-cinnamon-64bit.iso",
                size=3221225472,
                release_date=datetime(2024, 7, 25),
                description="Linux Mint 22 Cinnamon Edition - Based on Ubuntu 24.04 LTS",
                icon="🍃",
                source="Linux Mint",
            ),
            OSInfo(
                name="Linux Mint",
                version="21.3 \"Virginia\"",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://linuxmint.com/iso/stable/linuxmint-21.3-cinnamon-64bit.iso",
                size=3145728000,
                release_date=datetime(2024, 1, 15),
                description="Linux Mint 21.3 Cinnamon Edition - Based on Ubuntu 22.04 LTS",
                icon="🍃",
                source="Linux Mint",
            ),
        ]

        return self._apply_filters(isos, **filters)

    async def _fetch_arch_linux(self, **filters) -> List[OSInfo]:
        """Fetch Arch Linux ISO information."""
        isos = [
            OSInfo(
                name="Arch Linux",
                version="2024.12.01",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://archlinux.org/iso/2024.12.01/archlinux-2024.12.01-x86_64.iso",
                size=996147200,
                release_date=datetime(2024, 12, 1),
                description="Arch Linux - Rolling release, simple and lightweight",
                icon="🏔️",
                source="Arch Linux",
            ),
        ]

        return self._apply_filters(isos, **filters)

    async def _fetch_opensuse(self, **filters) -> List[OSInfo]:
        """Fetch openSUSE ISO information."""
        isos = [
            OSInfo(
                name="openSUSE Tumbleweed",
                version="Latest",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://download.opensuse.org/tumbleweed/iso/openSUSE-Tumbleweed-DVD-x86_64-Current.iso",
                size=4194304000,
                description="openSUSE Tumbleweed - Rolling release",
                icon="🦎",
                source="openSUSE",
            ),
            OSInfo(
                name="openSUSE Leap",
                version="15.6",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://download.opensuse.org/distribution/leap/15.6/iso/openSUSE-Leap-15.6-DVD-x86_64.iso",
                size=2684354560,
                release_date=datetime(2024, 6, 11),
                description="openSUSE Leap 15.6 - Enterprise-grade Linux",
                icon="🦎",
                source="openSUSE",
            ),
        ]

        return self._apply_filters(isos, **filters)

    def _apply_filters(self, isos: List[OSInfo], **filters) -> List[OSInfo]:
        """Apply filters to a list of OSInfo objects."""
        filtered = isos

        if "architecture" in filters:
            filtered = [iso for iso in filtered if iso.architecture == filters["architecture"]]

        if "language" in filters:
            filtered = [iso for iso in filtered if iso.language == filters["language"]]

        if "version" in filters:
            filtered = [iso for iso in filtered if filters["version"] in iso.version]

        if "name" in filters:
            filtered = [iso for iso in filtered if filters["name"].lower() in iso.name.lower()]

        return filtered
