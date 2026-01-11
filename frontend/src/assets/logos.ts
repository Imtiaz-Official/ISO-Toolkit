/**
 * Linux Distribution Logos
 * Using official logo sources for clean, modern appearance
 * SVG logos preferred for scalability and clean rendering
 */

export const linuxLogos: Record<string, { url: string; fallback: string }> = {
  // Ubuntu Family - Official Ubuntu logos
  "Ubuntu": {
    url: "https://assets.ubuntu.com/v1/73a4d93d-ubuntu-cof-orange.svg",
    fallback: "🟠"
  },
  "Kubuntu": {
    url: "https://assets.ubuntu.com/v1/751d5a7d-kubuntu-logo-a-2022.svg",
    fallback: "💙"
  },
  "Xubuntu": {
    url: "https://assets.ubuntu.com/v1/9aebfd65-xubuntu-logo-a.svg",
    fallback: "🦊"
  },
  "Lubuntu": {
    url: "https://assets.ubuntu.com/v1/e9a4d93d-lubuntu-logo-a.svg",
    fallback: "🐧"
  },
  "Ubuntu MATE": {
    url: "https://assets.ubuntu.com/v1/3a5a5a7d-ubuntu-mate-logo-a.svg",
    fallback: "💚"
  },
  "Ubuntu Studio": {
    url: "https://assets.ubuntu.com/v1/1a5a5a7d-ubuntustudio-logo-a.svg",
    fallback: "🎵"
  },
  "Edubuntu": {
    url: "https://assets.ubuntu.com/v1/2a5a5a7d-edubuntu-logo-a.svg",
    fallback: "🎓"
  },
  "Ubuntu Budgie": {
    url: "https://assets.ubuntu.com/v1/4a5a5a7d-ubuntu-budgie-logo-a.svg",
    fallback: "🦜"
  },
  "Ubuntu Cinnamon": {
    url: "https://assets.ubuntu.com/v1/5a5a5a7d-ubuntu-cinnamon-logo-a.svg",
    fallback: "🎄"
  },

  // Debian Family - Official logos
  "Debian": {
    url: "https://www.debian.org/Pics/debian-logo.svg",
    fallback: "🔴"
  },
  "Linux Mint": {
    url: "https://linuxmint.com/favicon.ico",
    fallback: "🍃"
  },
  "MX Linux": {
    url: "https://mxlinux.org/wp-content/uploads/mx-logo.svg",
    fallback: "🐴"
  },
  "antiX": {
    url: "https://antixlinux.com/wp-content/uploads/2022/09/antix-logo.svg",
    fallback: "🐜"
  },

  // Fedora / Red Hat Family - Official logos
  "Fedora": {
    url: "https://fedoraproject.org/static/images/fedora-logo.svg",
    fallback: "🔵"
  },
  "RHEL": {
    url: "https://www.redhat.com/rhdc/managed-files/brand-assets/RHLogo_White_Black.svg",
    fallback: "🎩"
  },
  "Rocky Linux": {
    url: "https://rockylinux.org/img/logo-dark.svg",
    fallback: "💎"
  },
  "AlmaLinux": {
    url: "https://almalinux.org/wp-content/uploads/2021/08/almalinux-logo-dark.svg",
    fallback: "🐦"
  },
  "CentOS Stream": {
    url: "https://www.centos.org/assets/img/centos-logo.svg",
    fallback: "📦"
  },

  // Arch Linux Family - Official logos
  "Arch Linux": {
    url: "https://archlinux.org/static/logo.svg",
    fallback: "🏔️"
  },
  "Manjaro": {
    url: "https://manjaro.org/static/logo.svg",
    fallback: "💚"
  },
  "EndeavourOS": {
    url: "https://endeavouros.com/wp-content/uploads/2021/09/endeavouros-logo.svg",
    fallback: "🚀"
  },
  "Garuda Linux": {
    url: "https://garudalinux.org/static/logo.svg",
    fallback: "🦅"
  },
  "Artix Linux": {
    url: "https://artixlinux.org/static/logo.svg",
    fallback: "🎨"
  },
  "ArcoLinux": {
    url: "https://arcolinux.com/static/logo.svg",
    fallback: "🎯"
  },

  // openSUSE Family - Official logos
  "openSUSE": {
    url: "https://en.opensuse.org/images/0/0b/Logo-geeko_head.svg",
    fallback: "🦎"
  },

  // Independent Distributions - Official logos
  "Pop!_OS": {
    url: "https://pop.system76.com/img/pop-logo.svg",
    fallback: "🚀"
  },
  "elementary OS": {
    url: "https://elementary.io/images/elementaryos_logo.svg",
    fallback: "💎"
  },
  "Zorin OS": {
    url: "https://zorinos.com/static/logo.svg",
    fallback: "🌟"
  },
  "Solus": {
    url: "https://getsol.us/images/logo.svg",
    fallback: "🌿"
  },
  "KDE neon": {
    url: "https://kde.org/images/stable/kslogo.svg",
    fallback: "💠"
  },
  "NixOS": {
    url: "https://nixos.org/logo/nixos-logo.svg",
    fallback: "🌱"
  },
  "Gentoo": {
    url: "https://www.gentoo.org/assets/img/logo/gentoo-logo.svg",
    fallback: "💜"
  },
  "Slackware": {
    url: "https://www.slackware.com/logo.svg",
    fallback: "🔷"
  },
  "Void Linux": {
    url: "https://voidlinux.org/assets/logo.svg",
    fallback: "⚫"
  },
  "Deepin": {
    url: "https://www.deepin.org/en/logo.svg",
    fallback: "🎨"
  },
  "Bodhi Linux": {
    url: "https://bodhilinux.com/static/logo.svg",
    fallback: "🌸"
  },
  "Q4OS": {
    url: "https://q4os.org/static/logo.svg",
    fallback: "🔵"
  },
  "PCLinuxOS": {
    url: "https://pclinuxos.com/static/logo.svg",
    fallback: "🌲"
  },
  "BigLinux": {
    url: "https://biglinux.com.br/static/logo.svg",
    fallback: "🇧🇷"
  },
  "RebeccaBlackOS": {
    url: "https://rebeccablackos.org/static/logo.svg",
    fallback: "🎬"
  },

  // Security Distributions - Official logos
  "Kali Linux": {
    url: "https://www.kali.org/images/kali-logo.svg",
    fallback: "🐉"
  },
  "Parrot OS": {
    url: "https://parrotsec.org/static/logo.svg",
    fallback: "🦜"
  },
  "Tails": {
    url: "https://tails.net/images/tails-logo.svg",
    fallback: "🕵️"
  },

  // Lightweight - Official logos
  "Puppy Linux": {
    url: "https://puppylinux.com/static/logo.svg",
    fallback: "🐕"
  },
};

/**
 * macOS Logos - Apple official logos
 */
export const macOSLogos: Record<string, { url: string; fallback: string }> = {
  "macOS Sequoia": {
    url: "https://developer.apple.com/assets/elements/icons/macos-logo_2x.png",
    fallback: "🍎"
  },
  "macOS Sonoma": {
    url: "https://developer.apple.com/assets/elements/icons/macos-logo_2x.png",
    fallback: "🍏"
  },
  "macOS Ventura": {
    url: "https://developer.apple.com/assets/elements/icons/macos-logo_2x.png",
    fallback: "🍐"
  },
  "macOS Monterey": {
    url: "https://developer.apple.com/assets/elements/icons/macos-logo_2x.png",
    fallback: "🌊"
  },
  "macOS Big Sur": {
    url: "https://developer.apple.com/assets/elements/icons/macos-logo_2x.png",
    fallback: "🏔️"
  },
  "macOS Catalina": {
    url: "https://developer.apple.com/assets/elements/icons/macos-logo_2x.png",
    fallback: "🐱"
  },
  "macOS Mojave": {
    url: "https://developer.apple.com/assets/elements/icons/macos-logo_2x.png",
    fallback: "🌵"
  },
  "macOS High Sierra": {
    url: "https://developer.apple.com/assets/elements/icons/macos-logo_2x.png",
    fallback: "⛰️"
  },
};

/**
 * BSD Distribution Logos - Official logos
 */
export const bsdLogos: Record<string, { url: string; fallback: string }> = {
  "FreeBSD": {
    url: "https://www.freebsd.org/logo/logo-full.svg",
    fallback: "😈"
  },
  "OpenBSD": {
    url: "https://www.openbsd.org/images/logo.svg",
    fallback: "🐡"
  },
  "NetBSD": {
    url: "https://www.netbsd.org/images/NetBSD-logo.svg",
    fallback: "👻"
  },
  "GhostBSD": {
    url: "https://ghostbsd.org/static/logo.svg",
    fallback: "👻"
  },
  "OPNsense": {
    url: "https://opnsense.org/static/logo.svg",
    fallback: "🔥"
  },
  "pfSense": {
    url: "https://www.pfsense.org/static/logo.svg",
    fallback: "🔒"
  },
  "DragonFly BSD": {
    url: "https://www.dragonflybsd.org/static/logo.svg",
    fallback: "🐉"
  },
  "DesktopBSD": {
    url: "https://www.desktopbsd.net/static/logo.svg",
    fallback: "🖥️"
  },
};

/**
 * Get logo URL for a Linux distribution
 */
export function getDistroLogo(distroName: string): string | undefined {
  return linuxLogos[distroName]?.url;
}

/**
 * Get fallback emoji for a Linux distribution
 */
export function getDistroFallback(distroName: string): string {
  return linuxLogos[distroName]?.fallback || "🐧";
}

/**
 * All available distributions
 */
export const allDistributions = Object.keys(linuxLogos);
