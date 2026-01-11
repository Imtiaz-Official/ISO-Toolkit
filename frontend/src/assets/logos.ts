/**
 * Linux Distribution Logos
 * Using official logo sources with local fallbacks
 * All logos are stored locally in /logos folder for reliability and performance
 */

// Import local logos
const logoPath = '/logos';

export const linuxLogos: Record<string, { url: string; fallback: string }> = {
  // Ubuntu Family - Official Ubuntu logos (local)
  "Ubuntu": {
    url: `${logoPath}/ubuntu.svg`,
    fallback: "🟠"
  },
  "Kubuntu": {
    url: `${logoPath}/kubuntu.svg`,
    fallback: "💙"
  },
  "Xubuntu": {
    url: `${logoPath}/xubuntu.svg`,
    fallback: "🦊"
  },
  "Lubuntu": {
    url: `${logoPath}/lubuntu.svg`,
    fallback: "🐧"
  },
  "Ubuntu MATE": {
    url: `${logoPath}/ubuntu-mate.svg`,
    fallback: "💚"
  },
  "Ubuntu Studio": {
    url: `${logoPath}/ubuntu-studio.svg`,
    fallback: "🎵"
  },
  "Edubuntu": {
    url: `${logoPath}/ubuntu.svg`, // Fallback to Ubuntu
    fallback: "🎓"
  },
  "Ubuntu Budgie": {
    url: `${logoPath}/ubuntu-budgie.svg`,
    fallback: "🦜"
  },
  "Ubuntu Cinnamon": {
    url: `${logoPath}/ubuntu-cinnamon.svg`,
    fallback: "🎄"
  },
  "KDE neon": {
    url: `${logoPath}/kde-neon.svg`,
    fallback: "💠"
  },

  // Debian Family - Official logos (local)
  "Debian": {
    url: `${logoPath}/debian.svg`,
    fallback: "🔴"
  },
  "Linux Mint": {
    url: `${logoPath}/linux-mint.svg`,
    fallback: "🍃"
  },
  "Linux Mint Cinnamon": {
    url: `${logoPath}/linux-mint.svg`,
    fallback: "🍃"
  },
  "Linux Mint MATE": {
    url: `${logoPath}/linux-mint.svg`,
    fallback: "🍃"
  },
  "Linux Mint XFCE": {
    url: `${logoPath}/linux-mint.svg`,
    fallback: "🍃"
  },
  "MX Linux": {
    url: `${logoPath}/mx-linux.svg`,
    fallback: "🐴"
  },
  "antiX": {
    url: `${logoPath}/antix.svg`,
    fallback: "🐜"
  },
  "Raspberry Pi OS": {
    url: `${logoPath}/raspberry-pi-os.svg`,
    fallback: "🍓"
  },

  // Fedora / Red Hat Family - Official logos (local)
  "Fedora": {
    url: `${logoPath}/fedora.svg`,
    fallback: "🔵"
  },
  "Fedora Workstation": {
    url: `${logoPath}/fedora.svg`,
    fallback: "🔵"
  },
  "Fedora KDE": {
    url: `${logoPath}/fedora.svg`,
    fallback: "🔵"
  },
  "Fedora XFCE": {
    url: `${logoPath}/fedora.svg`,
    fallback: "🔵"
  },
  "Fedora Server": {
    url: `${logoPath}/fedora.svg`,
    fallback: "🔵"
  },
  "Fedora Cinnamon": {
    url: `${logoPath}/fedora.svg`,
    fallback: "🔵"
  },
  "Fedora LXQt": {
    url: `${logoPath}/fedora.svg`,
    fallback: "🔵"
  },
  "Fedora ARM": {
    url: `${logoPath}/fedora.svg`,
    fallback: "🔵"
  },
  "RHEL": {
    url: `${logoPath}/rhel.svg`,
    fallback: "🎩"
  },
  "Rocky Linux": {
    url: `${logoPath}/rocky-linux.svg`,
    fallback: "💎"
  },
  "AlmaLinux": {
    url: `${logoPath}/almalinux.svg`,
    fallback: "🐦"
  },
  "CentOS Stream": {
    url: `${logoPath}/centos-stream.svg`,
    fallback: "📦"
  },
  "Oracle Linux": {
    url: `${logoPath}/oracle-linux.svg`,
    fallback: "🔴"
  },

  // Arch Linux Family - Official logos (local)
  "Arch Linux": {
    url: `${logoPath}/arch-linux.svg`,
    fallback: "🏔️"
  },
  "Manjaro": {
    url: `${logoPath}/manjaro.svg`,
    fallback: "💚"
  },
  "EndeavourOS": {
    url: `${logoPath}/endeavouros.svg`,
    fallback: "🚀"
  },
  "Garuda Linux": {
    url: `${logoPath}/garuda-linux.svg`,
    fallback: "🦅"
  },
  "Artix Linux": {
    url: `${logoPath}/artix-linux.svg`,
    fallback: "🎨"
  },
  "ArcoLinux": {
    url: `${logoPath}/arcolinux.svg`,
    fallback: "🎯"
  },

  // openSUSE Family - Official logos (local)
  "openSUSE": {
    url: `${logoPath}/opensuse.svg`,
    fallback: "🦎"
  },
  "openSUSE Leap": {
    url: `${logoPath}/opensuse-leap.svg`,
    fallback: "🦎"
  },
  "SUSE": {
    url: `${logoPath}/opensuse.svg`,
    fallback: "🦎"
  },

  // Independent Distributions - Official logos (local)
  "Pop!_OS": {
    url: `${logoPath}/pop-os.svg`,
    fallback: "🚀"
  },
  "elementary OS": {
    url: `${logoPath}/elementary-os.svg`,
    fallback: "💎"
  },
  "Zorin OS": {
    url: `${logoPath}/zorin-os.svg`,
    fallback: "🌟"
  },
  "Solus": {
    url: `${logoPath}/solus.svg`,
    fallback: "🌿"
  },
  "NixOS": {
    url: `${logoPath}/nixos.svg`,
    fallback: "🌱"
  },
  "Gentoo": {
    url: `${logoPath}/gentoo.svg`,
    fallback: "💜"
  },
  "Slackware": {
    url: `${logoPath}/slackware.svg`,
    fallback: "🔷"
  },
  "Void Linux": {
    url: `${logoPath}/void-linux.svg`,
    fallback: "⚫"
  },
  "Deepin": {
    url: `${logoPath}/deepin.svg`,
    fallback: "🎨"
  },
  "Bodhi Linux": {
    url: `${logoPath}/bodhi-linux.svg`,
    fallback: "🌸"
  },
  "Q4OS": {
    url: `${logoPath}/q4os.svg`,
    fallback: "🔵"
  },
  "PCLinuxOS": {
    url: `${logoPath}/pclinuxos.svg`,
    fallback: "🌲"
  },
  "DietPi": {
    url: `${logoPath}/dietpi.svg`,
    fallback: "🥗"
  },
  "LibreELEC": {
    url: `${logoPath}/libreelec.svg`,
    fallback: "📺"
  },
  "Clear Linux": {
    url: `${logoPath}/clear-linux.svg`,
    fallback: "💧"
  },
  "Mageia": {
    url: `${logoPath}/mageia.svg`,
    fallback: "🧙"
  },
  "Amazon Linux": {
    url: `${logoPath}/amazon-linux.svg`,
    fallback: "📦"
  },
  "BigLinux": {
    url: `${logoPath}/biglinux.svg`,
    fallback: "🇧🇷"
  },
  "RebeccaBlackOS": {
    url: `${logoPath}/rebecca-black-os.svg`,
    fallback: "🎬"
  },

  // Security Distributions - Official logos (local)
  "Kali Linux": {
    url: `${logoPath}/kali-linux.svg`,
    fallback: "🐉"
  },
  "Parrot OS": {
    url: `${logoPath}/parrot-os.svg`,
    fallback: "🦜"
  },
  "Tails": {
    url: `${logoPath}/tails.svg`,
    fallback: "🕵️"
  },

  // Lightweight - Official logos (local)
  "Alpine Linux": {
    url: `${logoPath}/alpine-linux.svg`,
    fallback: "🏔️"
  },
  "Puppy Linux": {
    url: `${logoPath}/puppy-linux.svg`,
    fallback: "🐕"
  },

  // ARM/SBC - Official logos (local)
  "Ubuntu MATE ARM": {
    url: `${logoPath}/ubuntu-logo.png`,
    fallback: "💚"
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
