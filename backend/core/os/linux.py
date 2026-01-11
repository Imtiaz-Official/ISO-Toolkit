"""
Linux OS provider - scrapers for Linux distribution ISO downloads.
"""

import asyncio
from typing import List, Optional
from datetime import datetime

from core.os.base import BaseProvider, ProviderMetadata
from core.models import OSInfo, OSCategory, Architecture


class LinuxProvider(BaseProvider):
    """
    Provider for Linux distribution ISO downloads.

    Supports 100+ Linux distributions including:
    - Ubuntu, Debian, and derivatives
    - Fedora, RHEL, and derivatives
    - Arch Linux and derivatives
    - openSUSE and SLES
    - Independent distributions
    """

    @property
    def metadata(self) -> ProviderMetadata:
        return ProviderMetadata(
            name="Linux",
            category=OSCategory.LINUX,
            description="Linux Distributions (100+ distributions available)",
            icon="🐧",
            enabled=True,
        )

    def get_supported_architectures(self) -> List[Architecture]:
        return [Architecture.X64, Architecture.X86, Architecture.ARM64, Architecture.ARM, Architecture.RISCV64]

    def get_supported_languages(self) -> List[str]:
        return ["Multi", "en-US", "en-GB"]

    async def fetch_available(self, **filters) -> List[OSInfo]:
        """Fetch all available Linux distribution ISOs."""
        all_isos = []

        # Fetch from all distros concurrently
        results = await asyncio.gather(
            self._fetch_ubuntu(**filters),
            self._fetch_kubuntu(**filters),
            self._fetch_xubuntu(**filters),
            self._fetch_lubuntu(**filters),
            self._fetch_ubuntumate(**filters),
            self._fetch_ubuntustudio(**filters),
            self._fetch_edubuntu(**filters),
            self._fetch_ubuntu_budgie(**filters),
            self._fetch_ubuntu_cinnamon(**filters),
            self._fetch_fedora(**filters),
            self._fetch_debian(**filters),
            self._fetch_linux_mint(**filters),
            self._fetch_arch_linux(**filters),
            self._fetch_manjaro(**filters),
            self._fetch_endeavour(**filters),
            self._fetch_garuda(**filters),
            self._fetch_opensuse(**filters),
            self._fetch_opensuse_leap(**filters),
            self._fetch_rhel(**filters),
            self._fetch_rocky(**filters),
            self._fetch_alma(**filters),
            self._fetch_centos_stream(**filters),
            self._fetch_pop_os(**filters),
            self._fetch_elementary(**filters),
            self._fetch_zorin(**filters),
            self._fetch_solus(**filters),
            self._fetch_mx_linux(**filters),
            self._fetch_kde_neon(**filters),
            self._fetch_nixos(**filters),
            self._fetch_gentoo(**filters),
            self._fetch_slackware(**filters),
            self._fetch_void(**filters),
            self._fetch_deepin(**filters),
            self._fetch_bodhi(**filters),
            self._fetch_q4os(**filters),
            self._fetch_pclinuxos(**filters),
            self._fetch_tails(**filters),
            self._fetch_kali(**filters),
            self._fetch_parrot(**filters),
            self._fetch_puppy(**filters),
            self._fetch_antix(**filters),
            self._fetch_artix(**filters),
            self._fetch_arcolinux(**filters),
            self._fetch_biglinux(**filters),
            self._fetch_rebecca(**filters),
            self._fetch_raspberry_pi_os(**filters),
            self._fetch_alpine(**filters),
            self._fetch_dietpi(**filters),
            self._fetch_libreelec(**filters),
            self._fetch_fedora_arm(**filters),
            self._fetch_ubuntu_mate_arm(**filters),
            self._fetch_oracle(**filters),
            self._fetch_amazon(**filters),
            self._fetch_clear(**filters),
            self._fetch_mageia(**filters),
            return_exceptions=True
        )

        for result in results:
            if isinstance(result, list):
                all_isos.extend(result)

        return all_isos

    async def _fetch_ubuntu(self, **filters) -> List[OSInfo]:
        """Fetch Ubuntu ISO information."""
        isos = [
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
                subcategory="Ubuntu",
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
                subcategory="Ubuntu",
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
                subcategory="Ubuntu",
            ),
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
                subcategory="Ubuntu",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_kubuntu(self, **filters) -> List[OSInfo]:
        """Fetch Kubuntu ISO information."""
        isos = [
            OSInfo(
                name="Kubuntu",
                version="24.04 LTS",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://cdimage.ubuntu.com/kubuntu/releases/24.04/release/kubuntu-24.04.3-desktop-amd64.iso",
                size=4194304000,
                release_date=datetime(2024, 8, 15),
                description="Kubuntu 24.04 LTS - Ubuntu with KDE Plasma",
                icon="💙",
                source="Kubuntu",
                subcategory="Kubuntu",
            ),
            OSInfo(
                name="Kubuntu",
                version="22.04 LTS",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://cdimage.ubuntu.com/kubuntu/releases/22.04/release/kubuntu-22.04.4-desktop-amd64.iso",
                size=3959422976,
                release_date=datetime(2024, 2, 23),
                description="Kubuntu 22.04 LTS - Ubuntu with KDE Plasma",
                icon="💙",
                source="Kubuntu",
                subcategory="Kubuntu",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_xubuntu(self, **filters) -> List[OSInfo]:
        """Fetch Xubuntu ISO information."""
        isos = [
            OSInfo(
                name="Xubuntu",
                version="24.04 LTS",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://cdimage.ubuntu.com/xubuntu/releases/24.04/release/xubuntu-24.04.3-desktop-amd64.iso",
                size=3670016000,
                release_date=datetime(2024, 8, 15),
                description="Xubuntu 24.04 LTS - Ubuntu with XFCE",
                icon="🦊",
                source="Xubuntu",
                subcategory="Xubuntu",
            ),
            OSInfo(
                name="Xubuntu",
                version="22.04 LTS",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://cdimage.ubuntu.com/xubuntu/releases/22.04/release/xubuntu-22.04.4-desktop-amd64.iso",
                size=3534162944,
                release_date=datetime(2024, 2, 23),
                description="Xubuntu 22.04 LTS - Ubuntu with XFCE",
                icon="🦊",
                source="Xubuntu",
                subcategory="Xubuntu",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_lubuntu(self, **filters) -> List[OSInfo]:
        """Fetch Lubuntu ISO information."""
        isos = [
            OSInfo(
                name="Lubuntu",
                version="24.04 LTS",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://cdimage.ubuntu.com/lubuntu/releases/24.04/release/lubuntu-24.04.3-desktop-amd64.iso",
                size=3221225472,
                release_date=datetime(2024, 8, 15),
                description="Lubuntu 24.04 LTS - Ubuntu with LXQt",
                icon="🐧",
                source="Lubuntu",
                subcategory="Lubuntu",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_ubuntumate(self, **filters) -> List[OSInfo]:
        """Fetch Ubuntu MATE ISO information."""
        isos = [
            OSInfo(
                name="Ubuntu MATE",
                version="24.04 LTS",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://cdimage.ubuntu.com/ubuntu-mate/releases/24.04/release/ubuntu-mate-24.04.3-desktop-amd64.iso",
                size=4194304000,
                release_date=datetime(2024, 8, 15),
                description="Ubuntu MATE 24.04 LTS - Ubuntu with MATE desktop",
                icon="💚",
                source="Ubuntu MATE",
                subcategory="Ubuntu MATE",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_ubuntustudio(self, **filters) -> List[OSInfo]:
        """Fetch Ubuntu Studio ISO information."""
        isos = [
            OSInfo(
                name="Ubuntu Studio",
                version="24.04 LTS",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://cdimage.ubuntu.com/ubuntustudio/releases/24.04/release/ubuntustudio-24.04.3-dvd-amd64.iso",
                size=5368709120,
                release_date=datetime(2024, 8, 15),
                description="Ubuntu Studio 24.04 LTS - For content creation",
                icon="🎵",
                source="Ubuntu Studio",
                subcategory="Ubuntu Studio",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_edubuntu(self, **filters) -> List[OSInfo]:
        """Fetch Edubuntu ISO information."""
        isos = [
            OSInfo(
                name="Edubuntu",
                version="24.04 LTS",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://cdimage.ubuntu.com/edubuntu/releases/24.04/release/edubuntu-24.04.3-desktop-amd64.iso",
                size=5153960755,
                release_date=datetime(2024, 8, 15),
                description="Edubuntu 24.04 LTS - For education",
                icon="🎓",
                source="Edubuntu",
                subcategory="Edubuntu",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_ubuntu_budgie(self, **filters) -> List[OSInfo]:
        """Fetch Ubuntu Budgie ISO information."""
        isos = [
            OSInfo(
                name="Ubuntu Budgie",
                version="24.04 LTS",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://cdimage.ubuntu.com/ubuntu-budgie/releases/24.04/release/ubuntu-budgie-24.04.3-desktop-amd64.iso",
                size=3984588800,
                release_date=datetime(2024, 8, 15),
                description="Ubuntu Budgie 24.04 LTS - Ubuntu with Budgie desktop",
                icon="🦜",
                source="Ubuntu Budgie",
                subcategory="Ubuntu Budgie",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_ubuntu_cinnamon(self, **filters) -> List[OSInfo]:
        """Fetch Ubuntu Cinnamon ISO information."""
        isos = [
            OSInfo(
                name="Ubuntu Cinnamon",
                version="24.04 LTS",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://github.com/Ubuntu-Cinnamon/remix/releases/download/24.04.1/ubuntu-cinnamon-24.04.1-desktop-amd64.iso",
                size=4246732800,
                release_date=datetime(2024, 8, 15),
                description="Ubuntu Cinnamon 24.04 LTS - Ubuntu with Cinnamon desktop",
                icon="🎄",
                source="Ubuntu Cinnamon Remix",
                subcategory="Ubuntu Cinnamon",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_fedora(self, **filters) -> List[OSInfo]:
        """Fetch Fedora ISO information."""
        isos = [
            # Fedora Workstation
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
                subcategory="Fedora",
            ),
            # Fedora Server
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
                subcategory="Fedora",
            ),
            # Fedora KDE Plasma
            OSInfo(
                name="Fedora KDE Plasma",
                version="41",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://download.fedoraproject.org/pub/fedora/linux/releases/41/Spins/x86_64/iso/Fedora-KDE-Live-x86_64-41-1.4.iso",
                size=2097152000,
                release_date=datetime(2024, 10, 29),
                description="Fedora 41 KDE Plasma - KDE desktop edition",
                icon="🔵",
                source="Fedora Project",
                subcategory="Fedora",
            ),
            # Fedora XFCE
            OSInfo(
                name="Fedora XFCE",
                version="41",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://download.fedoraproject.org/pub/fedora/linux/releases/41/Spins/x86_64/iso/Fedora-Xfce-Live-x86_64-41-1.4.iso",
                size=1468006400,
                release_date=datetime(2024, 10, 29),
                description="Fedora 41 XFCE - Lightweight XFCE desktop",
                icon="🔵",
                source="Fedora Project",
                subcategory="Fedora",
            ),
            # Fedora LXQt
            OSInfo(
                name="Fedora LXQt",
                version="41",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://download.fedoraproject.org/pub/fedora/linux/releases/41/Spins/x86_64/iso/Fedora-LXQt-Live-x86_64-41-1.4.iso",
                size=1363148800,
                release_date=datetime(2024, 10, 29),
                description="Fedora 41 LXQt - Ultra-lightweight desktop",
                icon="🔵",
                source="Fedora Project",
                subcategory="Fedora",
            ),
            # Fedora Cinnamon
            OSInfo(
                name="Fedora Cinnamon",
                version="41",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://download.fedoraproject.org/pub/fedora/linux/releases/41/Spins/x86_64/iso/Fedora-Cinnamon-Live-x86_64-41-1.4.iso",
                size=2097152000,
                release_date=datetime(2024, 10, 29),
                description="Fedora 41 Cinnamon - Cinnamon desktop edition",
                icon="🔵",
                source="Fedora Project",
                subcategory="Fedora",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_debian(self, **filters) -> List[OSInfo]:
        """Fetch Debian ISO information."""
        isos = [
            OSInfo(
                name="Debian",
                version="13.2 Trixie",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-13.2.0-amd64-netinst.iso",
                size=419430400,
                release_date=datetime(2024, 11, 9),
                description="Debian 13.2 Trixie - Network install",
                icon="🔴",
                source="Debian",
                subcategory="Debian",
            ),
            OSInfo(
                name="Debian",
                version="13.2 Trixie",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://cdimage.debian.org/debian-cd/current/amd64/iso-dvd/debian-13.2.0-amd64-DVD-1.iso",
                size=4194304000,
                release_date=datetime(2024, 11, 9),
                description="Debian 13.2 Trixie - Full DVD",
                icon="🔴",
                source="Debian",
                subcategory="Debian",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_linux_mint(self, **filters) -> List[OSInfo]:
        """Fetch Linux Mint ISO information.

        Using reliable mirror sources for Linux Mint downloads.
        """
        isos = [
            # Linux Mint 22 Cinnamon
            OSInfo(
                name="Linux Mint Cinnamon",
                version="22 \"Wilma\"",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://mirrors.kernel.org/linuxmint/stable/22/linuxmint-22-cinnamon-64bit.iso",
                mirrors=[
                    "https://ftp.heanet.ie/mirrors/linuxmint.com/stable/22/linuxmint-22-cinnamon-64bit.iso",
                    "https://mirror.math.princeton.edu/pub/linuxmint-stable/22/linuxmint-22-cinnamon-64bit.iso",
                ],
                size=3221225472,
                release_date=datetime(2024, 7, 25),
                description="Linux Mint 22 Cinnamon Edition - Based on Ubuntu 24.04 LTS",
                icon="🍃",
                source="Linux Mint",
                subcategory="Linux Mint",
            ),
            # Linux Mint 22 MATE
            OSInfo(
                name="Linux Mint MATE",
                version="22 \"Wilma\"",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://mirrors.kernel.org/linuxmint/stable/22/linuxmint-22-mate-64bit.iso",
                mirrors=[
                    "https://ftp.heanet.ie/mirrors/linuxmint.com/stable/22/linuxmint-22-mate-64bit.iso",
                    "https://mirror.math.princeton.edu/pub/linuxmint-stable/22/linuxmint-22-mate-64bit.iso",
                ],
                size=3061841920,
                release_date=datetime(2024, 7, 25),
                description="Linux Mint 22 MATE Edition - Based on Ubuntu 24.04 LTS",
                icon="🍃",
                source="Linux Mint",
                subcategory="Linux Mint",
            ),
            # Linux Mint 22 XFCE
            OSInfo(
                name="Linux Mint XFCE",
                version="22 \"Wilma\"",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://mirrors.kernel.org/linuxmint/stable/22/linuxmint-22-xfce-64bit.iso",
                mirrors=[
                    "https://ftp.heanet.ie/mirrors/linuxmint.com/stable/22/linuxmint-22-xfce-64bit.iso",
                    "https://mirror.math.princeton.edu/pub/linuxmint-stable/22/linuxmint-22-xfce-64bit.iso",
                ],
                size=2894069760,
                release_date=datetime(2024, 7, 25),
                description="Linux Mint 22 XFCE Edition - Based on Ubuntu 24.04 LTS",
                icon="🍃",
                source="Linux Mint",
                subcategory="Linux Mint",
            ),
            # Linux Mint 21.3 Cinnamon
            OSInfo(
                name="Linux Mint Cinnamon",
                version="21.3 \"Virginia\"",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://mirrors.kernel.org/linuxmint/stable/21.3/linuxmint-21.3-cinnamon-64bit.iso",
                mirrors=[
                    "https://ftp.heanet.ie/mirrors/linuxmint.com/stable/21.3/linuxmint-21.3-cinnamon-64bit.iso",
                ],
                size=3145728000,
                release_date=datetime(2024, 1, 15),
                description="Linux Mint 21.3 Cinnamon Edition - Based on Ubuntu 22.04 LTS",
                icon="🍃",
                source="Linux Mint",
                subcategory="Linux Mint",
            ),
            # Linux Mint 21.3 MATE
            OSInfo(
                name="Linux Mint MATE",
                version="21.3 \"Virginia\"",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://mirrors.kernel.org/linuxmint/stable/21.3/linuxmint-21.3-mate-64bit.iso",
                mirrors=[
                    "https://ftp.heanet.ie/mirrors/linuxmint.com/stable/21.3/linuxmint-21.3-mate-64bit.iso",
                ],
                size=2988446720,
                release_date=datetime(2024, 1, 15),
                description="Linux Mint 21.3 MATE Edition - Based on Ubuntu 22.04 LTS",
                icon="🍃",
                source="Linux Mint",
                subcategory="Linux Mint",
            ),
            # Linux Mint 21.3 XFCE
            OSInfo(
                name="Linux Mint XFCE",
                version="21.3 \"Virginia\"",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://mirrors.kernel.org/linuxmint/stable/21.3/linuxmint-21.3-xfce-64bit.iso",
                mirrors=[
                    "https://ftp.heanet.ie/mirrors/linuxmint.com/stable/21.3/linuxmint-21.3-xfce-64bit.iso",
                ],
                size=2810183680,
                release_date=datetime(2024, 1, 15),
                description="Linux Mint 21.3 XFCE Edition - Based on Ubuntu 22.04 LTS",
                icon="🍃",
                source="Linux Mint",
                subcategory="Linux Mint",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_arch_linux(self, **filters) -> List[OSInfo]:
        """Fetch Arch Linux ISO information."""
        isos = [
            OSInfo(
                name="Arch Linux",
                version="2026.01.01",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://archlinux.org/iso/2026.01.01/archlinux-2026.01.01-x86_64.iso",
                size=996147200,
                release_date=datetime(2026, 1, 1),
                description="Arch Linux - Rolling release, simple and lightweight",
                icon="🏔️",
                source="Arch Linux",
                subcategory="Arch Linux",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_manjaro(self, **filters) -> List[OSInfo]:
        """Fetch Manjaro Linux ISO information."""
        isos = [
            OSInfo(
                name="Manjaro",
                version="24.0",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://download.manjaro.org/xfce/24.0/manjaro-xfce-24.0-240513-linux515.iso",
                size=3221225472,
                release_date=datetime(2024, 5, 13),
                description="Manjaro 24.0 XFCE Edition - Arch-based with XFCE",
                icon="💚",
                source="Manjaro",
                subcategory="Manjaro",
            ),
            OSInfo(
                name="Manjaro GNOME",
                version="24.0",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://download.manjaro.org/gnome/24.0/manjaro-gnome-24.0-240513-linux515.iso",
                size=3489660928,
                release_date=datetime(2024, 5, 13),
                description="Manjaro 24.0 GNOME Edition - Modern GNOME desktop",
                icon="💚",
                source="Manjaro",
                subcategory="Manjaro",
            ),
            OSInfo(
                name="Manjaro KDE",
                version="24.0",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://download.manjaro.org/kde/24.0/manjaro-kde-24.0-240513-linux515.iso",
                size=3690987520,
                release_date=datetime(2024, 5, 13),
                description="Manjaro 24.0 KDE Plasma Edition - Feature-rich KDE",
                icon="💚",
                source="Manjaro",
                subcategory="Manjaro",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_endeavour(self, **filters) -> List[OSInfo]:
        """Fetch EndeavourOS ISO information."""
        isos = [
            OSInfo(
                name="EndeavourOS",
                version="2024.08",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://github.com/endeavouros-team/ISO/releases/download/2024.08.05/EndeavourOS-2024.08.05-x86_64.iso",
                size=2548039680,
                release_date=datetime(2024, 8, 5),
                description="EndeavourOS 2024.08 - Arch-based with XFCE",
                icon="🚀",
                source="EndeavourOS",
                subcategory="EndeavourOS",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_garuda(self, **filters) -> List[OSInfo]:
        """Fetch Garuda Linux ISO information."""
        isos = [
            OSInfo(
                name="Garuda Dr460nized",
                version="Latest",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://iso.garudalinux.org/ee/git-latest/garuda-dr460nized-linux.iso",
                size=4194304000,
                description="Garuda Dr460nized - Arch-based with KDE and tweaks",
                icon="🦅",
                source="Garuda Linux",
                subcategory="Garuda Linux",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_opensuse(self, **filters) -> List[OSInfo]:
        """Fetch openSUSE Tumbleweed ISO information."""
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
                subcategory="openSUSE",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_opensuse_leap(self, **filters) -> List[OSInfo]:
        """Fetch openSUSE Leap ISO information."""
        isos = [
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
                subcategory="openSUSE",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_rhel(self, **filters) -> List[OSInfo]:
        """Fetch Red Hat Enterprise Linux ISO information."""
        isos = [
            OSInfo(
                name="Red Hat Enterprise Linux",
                version="9.4",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://access.redhat.com/downloads/content/rhel/9.4/latest/x86_64/iso",
                size=0,
                release_date=datetime(2024, 5, 1),
                description="RHEL 9.4 - Enterprise Linux (requires subscription)",
                icon="🎩",
                source="Red Hat",
                subcategory="RHEL",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_rocky(self, **filters) -> List[OSInfo]:
        """Fetch Rocky Linux ISO information."""
        isos = [
            OSInfo(
                name="Rocky Linux",
                version="9.4",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://download.rockylinux.org/pub/rocky/9.4/isos/x86_64/Rocky-9.4-x86_64-minimal.iso",
                size=2097152000,
                release_date=datetime(2024, 5, 1),
                description="Rocky Linux 9.4 - RHEL compatible",
                icon="💎",
                source="Rocky Enterprise",
                subcategory="Rocky Linux",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_alma(self, **filters) -> List[OSInfo]:
        """Fetch AlmaLinux ISO information."""
        isos = [
            OSInfo(
                name="AlmaLinux",
                version="9.4",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://repo.almalinux.org/almalinux/9.4/isos/x86_64/AlmaLinux-9.4-x86_64-minimal.iso",
                size=2097152000,
                release_date=datetime(2024, 5, 1),
                description="AlmaLinux 9.4 - RHEL compatible",
                icon="🐦",
                source="AlmaLinux OS Foundation",
                subcategory="AlmaLinux",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_centos_stream(self, **filters) -> List[OSInfo]:
        """Fetch CentOS Stream ISO information."""
        isos = [
            OSInfo(
                name="CentOS Stream",
                version="9",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://mirrors.centos.org/mirrorlist?path=/9-stream/BaseOS/x86_64/iso/CentOS-Stream-9-latest-x86_64-boot.iso",
                size=2097152000,
                description="CentOS Stream 9 - RHEL upstream",
                icon="📦",
                source="CentOS",
                subcategory="CentOS Stream",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_pop_os(self, **filters) -> List[OSInfo]:
        """Fetch Pop!_OS ISO information."""
        isos = [
            OSInfo(
                name="Pop!_OS",
                version="24.04 LTS",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://pop-iso.s3.amazonaws.com/24.04/amd64/nvidia/6/pop-os-24.04-amd64-nvidia-6108.iso",
                size=3865470592,
                release_date=datetime(2024, 10, 8),
                description="Pop!_OS 24.04 LTS - By System76 with NVIDIA",
                icon="🚀",
                source="System76",
                subcategory="Pop!_OS",
            ),
            OSInfo(
                name="Pop!_OS",
                version="24.04 LTS",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://pop-iso.s3.amazonaws.com/24.04/amd64/intel/6/pop-os-24.04-amd64-intel-6108.iso",
                size=3732930560,
                release_date=datetime(2024, 10, 8),
                description="Pop!_OS 24.04 LTS - By System76 with Intel/AMD",
                icon="🚀",
                source="System76",
                subcategory="Pop!_OS",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_elementary(self, **filters) -> List[OSInfo]:
        """Fetch elementary OS ISO information."""
        isos = [
            OSInfo(
                name="elementary OS",
                version="8",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://github.com/elementary/os/releases/download/8.0/elementaryos-8.0-stable.2024-amd64.iso",
                size=3670016000,
                release_date=datetime(2024, 9, 1),
                description="elementary OS 8 - Beautiful and user-friendly",
                icon="💎",
                source="elementary",
                subcategory="elementary OS",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_zorin(self, **filters) -> List[OSInfo]:
        """Fetch Zorin OS ISO information."""
        isos = [
            OSInfo(
                name="Zorin OS Pro",
                version="17.2",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://releases.zorinos.com/17.2/zorin-17.2-pro-64.iso",
                size=5368709120,
                release_date=datetime(2024, 12, 1),
                description="Zorin OS 17.2 Pro - Premium edition",
                icon="🌟",
                source="Zorin Group",
                subcategory="Zorin OS",
            ),
            OSInfo(
                name="Zorin OS Core",
                version="17.2",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://releases.zorinos.com/17.2/zorin-17.2-core-64.iso",
                size=3103784960,
                release_date=datetime(2024, 12, 1),
                description="Zorin OS 17.2 Core - Free edition",
                icon="🌟",
                source="Zorin Group",
                subcategory="Zorin OS",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_solus(self, **filters) -> List[OSInfo]:
        """Fetch Solus ISO information."""
        isos = [
            OSInfo(
                name="Solus",
                version="5.0",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://getsol.us/downloads/5.0/solus-5.0-plasma.iso",
                size=2097152000,
                release_date=datetime(2024, 8, 1),
                description="Solus 5.0 - Built from scratch",
                icon="🌿",
                source="Solus Project",
                subcategory="Solus",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_mx_linux(self, **filters) -> List[OSInfo]:
        """Fetch MX Linux ISO information."""
        isos = [
            OSInfo(
                name="MX Linux",
                version="23.4",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://sourceforge.net/projects/mx-linux/files/Final/MX-23.4_x64.iso/download",
                size=1610612736,
                release_date=datetime(2024, 8, 1),
                description="MX Linux 23.4 - Midweight XFCE desktop",
                icon="🐴",
                source="MX Linux",
                subcategory="MX Linux",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_kde_neon(self, **filters) -> List[OSInfo]:
        """Fetch KDE neon ISO information."""
        isos = [
            OSInfo(
                name="KDE neon",
                version="User Edition",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://files.kde.org/neon/images/user/current/neon-user-current.iso",
                size=3221225472,
                description="KDE neon User Edition - Latest KDE Plasma on Ubuntu",
                icon="💠",
                source="KDE",
                subcategory="KDE neon",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_nixos(self, **filters) -> List[OSInfo]:
        """Fetch NixOS ISO information."""
        isos = [
            OSInfo(
                name="NixOS",
                version="24.11",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://channels.nixos.org/nixos-24.11/latest-nixos-minimal-x86_64-linux.iso",
                size=1073741824,
                description="NixOS 24.11 - Declarative Linux distribution",
                icon="🌱",
                source="NixOS",
                subcategory="NixOS",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_gentoo(self, **filters) -> List[OSInfo]:
        """Fetch Gentoo Linux ISO information."""
        isos = [
            OSInfo(
                name="Gentoo",
                version="Live",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://distfiles.gentoo.org/releases/amd64/autobuilds/current-live-amd64/admincd-amd64-20240901.iso",
                size=419430400,
                description="Gentoo Live - For installing Gentoo",
                icon="💜",
                source="Gentoo",
                subcategory="Gentoo",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_slackware(self, **filters) -> List[OSInfo]:
        """Fetch Slackware Linux ISO information."""
        isos = [
            OSInfo(
                name="Slackware",
                version="15.0",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="en-US",
                url="http://ftp.slackware.com/pub/slackware/slackware64-15.0-iso/slackware64-15.0-install-dvd.iso",
                size=2684354560,
                description="Slackware 15.0 - The oldest surviving Linux distribution",
                icon="🔷",
                source="Slackware",
                subcategory="Slackware",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_void(self, **filters) -> List[OSInfo]:
        """Fetch Void Linux ISO information."""
        isos = [
            OSInfo(
                name="Void Linux",
                version="Live",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://repo-default.voidlinux.org/live/20241001/void-live-x86_64-20241001.iso",
                size=734003200,
                description="Void Linux - Rolling release with XBPS",
                icon="⚫",
                source="Void Linux",
                subcategory="Void Linux",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_deepin(self, **filters) -> List[OSInfo]:
        """Fetch Deepin ISO information."""
        isos = [
            OSInfo(
                name="Deepin",
                version="23",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://cdn.deepin.org/releases/23/deepin-desktop-community-23-amd64.iso",
                size=3670016000,
                description="Deepin 23 - Beautiful desktop from China",
                icon="🎨",
                source="Deepin",
                subcategory="Deepin",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_bodhi(self, **filters) -> List[OSInfo]:
        """Fetch Bodhi Linux ISO information."""
        isos = [
            OSInfo(
                name="Bodhi Linux",
                version="7.0",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://downloads.sourceforge.net/project/bodhilinux/7.0.0/bodhi-7.0.0-64.iso",
                size=996147200,
                description="Bodhi Linux 7.0 - Minimalist with Moksha desktop",
                icon="🌸",
                source="Bodhi Linux",
                subcategory="Bodhi Linux",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_q4os(self, **filters) -> List[OSInfo]:
        """Fetch Q4OS ISO information."""
        isos = [
            OSInfo(
                name="Q4OS",
                version="5",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://downloads.sourceforge.net/project/q4os/q4os-5.1/x86_64/q4os-5.1-x86_64.iso",
                size=1610612736,
                description="Q4OS 5 - Lightweight and stable",
                icon="🔵",
                source="Q4OS",
                subcategory="Q4OS",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_pclinuxos(self, **filters) -> List[OSInfo]:
        """Fetch PCLinuxOS ISO information."""
        isos = [
            OSInfo(
                name="PCLinuxOS",
                version="KDE",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://iso.pclinuxos.com/pclos-iso/pclos-kde-darkstar-2024.08.iso",
                size=2097152000,
                description="PCLinuxOS KDE - User-friendly",
                icon="🌲",
                source="PCLinuxOS",
                subcategory="PCLinuxOS",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_tails(self, **filters) -> List[OSInfo]:
        """Fetch Tails ISO information."""
        isos = [
            OSInfo(
                name="Tails",
                version="6.0",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://download.tails.net/tails/stable/tails-amd64-6.0/tails-amd64-6.0.iso",
                size=1342177280,
                description="Tails 6.0 - The amnesic incognito live system",
                icon="🕵️",
                source="Tails",
                subcategory="Tails",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_kali(self, **filters) -> List[OSInfo]:
        """Fetch Kali Linux ISO information."""
        isos = [
            OSInfo(
                name="Kali Linux",
                version="2024.3",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://cdimage.kali.org/kali-2024.3/kali-linux-2024.3-installer-amd64.iso",
                size=2097152000,
                description="Kali Linux 2024.3 - Penetration testing",
                icon="🐉",
                source="OffSec",
                subcategory="Kali Linux",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_parrot(self, **filters) -> List[OSInfo]:
        """Fetch Parrot OS ISO information."""
        isos = [
            OSInfo(
                name="Parrot OS",
                version="6.0",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://download.parrotsec.org/iso/6.0/Parrot-security-6.0_amd64.iso",
                size=3221225472,
                description="Parrot OS 6.0 - Security and privacy",
                icon="🦜",
                source="Parrot Security",
                subcategory="Parrot OS",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_puppy(self, **filters) -> List[OSInfo]:
        """Fetch Puppy Linux ISO information."""
        isos = [
            OSInfo(
                name="Puppy Linux",
                version="Slacko",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://distro.ibiblio.org/puppylinux/puppylinux/slacko-6.3/slacko-6.3.0-uefi.iso",
                size=314572800,
                description="Puppy Linux Slacko - Ultra lightweight",
                icon="🐕",
                source="Puppy Linux",
                subcategory="Puppy Linux",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_antix(self, **filters) -> List[OSInfo]:
        """Fetch antiX Linux ISO information."""
        isos = [
            OSInfo(
                name="antiX",
                version="23",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://mirror.antixlinux.com/antix/23/antix-23-x64-full.iso",
                size=1610612736,
                description="antiX 23 - systemd-free",
                icon="🐜",
                source="antiX",
                subcategory="antiX",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_artix(self, **filters) -> List[OSInfo]:
        """Fetch Artix Linux ISO information."""
        isos = [
            OSInfo(
                name="Artix Linux",
                version="Live",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://mirror1.artixlinux.org/iso/2024.09/artix-linux-x86_64-openrc-20240930.iso",
                size=891289600,
                description="Artix Linux - Arch without systemd",
                icon="🎨",
                source="Artix Linux",
                subcategory="Artix Linux",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_arcolinux(self, **filters) -> List[OSInfo]:
        """Fetch ArcoLinux ISO information."""
        isos = [
            OSInfo(
                name="ArcoLinux",
                version="24.10",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://sourceforge.net/projects/arcolinux-community-edition/files/24.10/arco-community-2024.10.01-x86_64.iso/download",
                size=2097152000,
                description="ArcoLinux 24.10 - Arch-based with customization",
                icon="🎯",
                source="ArcoLinux",
                subcategory="ArcoLinux",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_biglinux(self, **filters) -> List[OSInfo]:
        """Fetch BigLinux ISO information."""
        isos = [
            OSInfo(
                name="BigLinux",
                version="24",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://biglinux.com.br/downloads/BigLinux-24.01-x86_64.iso",
                size=2899102924,
                description="BigLinux 24 - Brazilian distribution",
                icon="🇧🇷",
                source="BigLinux",
                subcategory="BigLinux",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_rebecca(self, **filters) -> List[OSInfo]:
        """Fetch RebeccaBlackOS ISO information."""
        isos = [
            OSInfo(
                name="RebeccaBlackOS",
                version="Live",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://rebeccablackos.org/download/rb-os-latest.iso",
                size=2097152000,
                description="RebeccaBlackOS - Rolling release",
                icon="🎬",
                source="RebeccaBlackOS",
                subcategory="RebeccaBlackOS",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_raspberry_pi_os(self, **filters) -> List[OSInfo]:
        """Fetch Raspberry Pi OS ISO information."""
        isos = [
            OSInfo(
                name="Raspberry Pi OS",
                version="Bookworm (64-bit)",
                category=OSCategory.LINUX,
                architecture=Architecture.ARM64,
                language="en-GB",
                url="https://downloads.raspberrypi.com/raspios_lite_arm64/images/raspios_lite_arm64-2024-03-15/2024-03-15-raspios-bookworm-arm64-lite.img.xz",
                size=482344960,
                release_date=datetime(2024, 3, 15),
                description="Raspberry Pi OS Lite 64-bit - Debian-based for Raspberry Pi 4/5",
                icon="🍓",
                source="Raspberry Pi Foundation",
                subcategory="Raspberry Pi OS",
            ),
            OSInfo(
                name="Raspberry Pi OS",
                version="Bookworm (32-bit)",
                category=OSCategory.LINUX,
                architecture=Architecture.ARM,
                language="en-GB",
                url="https://downloads.raspberrypi.com/raspios_lite_armhf/images/raspios_lite_armhf-2024-03-15/2024-03-15-raspios-bookworm-armhf-lite.img.xz",
                size=445644800,
                release_date=datetime(2024, 3, 15),
                description="Raspberry Pi OS Lite 32-bit - For all Raspberry Pi models",
                icon="🍓",
                source="Raspberry Pi Foundation",
                subcategory="Raspberry Pi OS",
            ),
            OSInfo(
                name="Raspberry Pi OS",
                version="Bookworm Desktop (64-bit)",
                category=OSCategory.LINUX,
                architecture=Architecture.ARM64,
                language="en-GB",
                url="https://downloads.raspberrypi.com/raspios_arm64/images/raspios_arm64-2024-03-15/2024-03-15-raspios-bookworm-arm64.img.xz",
                size=3103784960,
                release_date=datetime(2024, 3, 15),
                description="Raspberry Pi OS Desktop 64-bit - With PIXEL desktop",
                icon="🍓",
                source="Raspberry Pi Foundation",
                subcategory="Raspberry Pi OS",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_alpine(self, **filters) -> List[OSInfo]:
        """Fetch Alpine Linux ISO information."""
        isos = [
            OSInfo(
                name="Alpine Linux",
                version="3.20",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://dl-cdn.alpinelinux.org/alpine/v3.20/releases/x86_64/alpine-standard-3.20.0-x86_64.iso",
                size=161061273,
                release_date=datetime(2024, 7, 1),
                description="Alpine Linux 3.20 - Security-oriented, lightweight",
                icon="🏔️",
                source="Alpine Linux",
                subcategory="Alpine Linux",
            ),
            OSInfo(
                name="Alpine Linux",
                version="3.20",
                category=OSCategory.LINUX,
                architecture=Architecture.ARM64,
                language="Multi",
                url="https://dl-cdn.alpinelinux.org/alpine/v3.20/releases/aarch64/alpine-standard-3.20.0-aarch64.iso",
                size=147456000,
                release_date=datetime(2024, 7, 1),
                description="Alpine Linux 3.20 ARM64 - For ARM devices",
                icon="🏔️",
                source="Alpine Linux",
                subcategory="Alpine Linux",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_dietpi(self, **filters) -> List[OSInfo]:
        """Fetch DietPi ISO information."""
        isos = [
            OSInfo(
                name="DietPi",
                version="9.0",
                category=OSCategory.LINUX,
                architecture=Architecture.ARM64,
                language="Multi",
                url="https://dietpi.com/downloads/images/DietPi_RPi-ARMv8-Bullseye.img.xz",
                size=524288000,
                release_date=datetime(2024, 8, 1),
                description="DietPi 9.0 - Minimal OS for SBCs (Raspberry Pi)",
                icon="🥗",
                source="DietPi",
                subcategory="DietPi",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_libreelec(self, **filters) -> List[OSInfo]:
        """Fetch LibreELEC ISO information."""
        isos = [
            OSInfo(
                name="LibreELEC",
                version="12.0",
                category=OSCategory.LINUX,
                architecture=Architecture.ARM64,
                language="Multi",
                url="https://releases.libreelec.tv/LibreELEC-12.0.1/RPi4.arm/LibreELEC-RPi4.arm-12.0.1.img.gz",
                size=471859200,
                release_date=datetime(2024, 11, 1),
                description="LibreELEC 12.0 - Kodi for Raspberry Pi 4/5",
                icon="📺",
                source="LibreELEC",
                subcategory="LibreELEC",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_fedora_arm(self, **filters) -> List[OSInfo]:
        """Fetch Fedora ARM ISO information."""
        isos = [
            OSInfo(
                name="Fedora ARM",
                version="41",
                category=OSCategory.LINUX,
                architecture=Architecture.ARM64,
                language="Multi",
                url="https://download.fedoraproject.org/pub/fedora/linux/releases/41/Everything/aarch64/iso/Fedora-Everything-41-1.4-aarch64.iso",
                size=3690987520,
                release_date=datetime(2024, 10, 29),
                description="Fedora 41 ARM64 - For Raspberry Pi 4/5 and other ARM",
                icon="🔵",
                source="Fedora Project",
                subcategory="Fedora ARM",
            ),
            OSInfo(
                name="Fedora Server ARM",
                version="41",
                category=OSCategory.LINUX,
                architecture=Architecture.ARM64,
                language="Multi",
                url="https://download.fedoraproject.org/pub/fedora/linux/releases/41/Server/aarch64/iso/Fedora-Server-dvd-aarch64-41-1.4.iso",
                size=3221225472,
                release_date=datetime(2024, 10, 29),
                description="Fedora 41 Server ARM64 - For ARM servers",
                icon="🔵",
                source="Fedora Project",
                subcategory="Fedora ARM",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_ubuntu_mate_arm(self, **filters) -> List[OSInfo]:
        """Fetch Ubuntu MATE ARM ISO information."""
        isos = [
            OSInfo(
                name="Ubuntu MATE",
                version="24.04 LTS",
                category=OSCategory.LINUX,
                architecture=Architecture.ARM64,
                language="Multi",
                url="https://cdimage.ubuntu.com/ubuntu-mate/releases/24.04/release/ubuntu-mate-24.04-preinstalled-desktop-arm64+raspi.img.xz",
                size=4194304000,
                release_date=datetime(2024, 4, 25),
                description="Ubuntu MATE 24.04 LTS ARM64 - For Raspberry Pi 4/5",
                icon="💚",
                source="Ubuntu MATE",
                subcategory="Ubuntu MATE",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_oracle(self, **filters) -> List[OSInfo]:
        """Fetch Oracle Linux ISO information."""
        isos = [
            OSInfo(
                name="Oracle Linux",
                version="9.4",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://yum.oracle.com/ISOS/OracleLinux-R9-U4-x86_64-dvd.iso",
                size=11596411699,
                release_date=datetime(2024, 11, 1),
                description="Oracle Linux 9.4 - Free, enterprise-grade",
                icon="🔴",
                source="Oracle",
                subcategory="Oracle Linux",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_amazon(self, **filters) -> List[OSInfo]:
        """Fetch Amazon Linux ISO information."""
        isos = [
            OSInfo(
                name="Amazon Linux",
                version="2023.5",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="en-US",
                url="https://cdn.amazonlinux.com/os-images/2023.5.20241004/kvm/amzn2-kvm-2.0.20241004-x86_64.xfs.gpt.iso",
                size=1048576000,
                release_date=datetime(2024, 10, 4),
                description="Amazon Linux 2023.5 - For AWS",
                icon="📦",
                source="AWS",
                subcategory="Amazon Linux",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_clear(self, **filters) -> List[OSInfo]:
        """Fetch Clear Linux ISO information."""
        isos = [
            OSInfo(
                name="Clear Linux OS",
                version="Latest",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://cdn.download.clearlinux.org/releases/current/clear-latest-live-desktop.iso.xz",
                size=1887436800,
                description="Clear Linux OS - Intel-optimized",
                icon="💧",
                source="Clear Linux",
                subcategory="Clear Linux",
            ),
        ]
        return self._apply_filters(isos, **filters)

    async def _fetch_mageia(self, **filters) -> List[OSInfo]:
        """Fetch Mageia ISO information."""
        isos = [
            OSInfo(
                name="Mageia",
                version="9",
                category=OSCategory.LINUX,
                architecture=Architecture.X64,
                language="Multi",
                url="https://mirrors.kernel.org/mageia/distrib/9/iso/Mageia-9-x86_64.iso",
                size=3690987520,
                release_date=datetime(2024, 8, 1),
                description="Mageia 9 - Community Linux",
                icon="🧙",
                source="Mageia",
                subcategory="Mageia",
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

        if "name" in filters and filters["name"] is not None:
            filtered = [iso for iso in filtered if filters["name"].lower() in iso.name.lower()]

        return filtered
