/**
 * Linux Distribution Logos
 * Using reliable CDN sources - falling back to emojis for unavailable logos
 */

export const linuxLogos: Record<string, { url: string; fallback: string }> = {
  // Ubuntu Family - Using emojis (logo URLs unreliable)
  "Ubuntu": {
    url: "", // Use emoji fallback
    fallback: "🟠"
  },
  "Kubuntu": {
    url: "",
    fallback: "💙"
  },
  "Xubuntu": {
    url: "",
    fallback: "🦊"
  },
  "Lubuntu": {
    url: "",
    fallback: "🐧"
  },
  "Ubuntu MATE": {
    url: "",
    fallback: "💚"
  },
  "Ubuntu Studio": {
    url: "",
    fallback: "🎵"
  },
  "Edubuntu": {
    url: "",
    fallback: "🎓"
  },
  "Ubuntu Budgie": {
    url: "",
    fallback: "🦜"
  },
  "Ubuntu Cinnamon": {
    url: "",
    fallback: "🎄"
  },

  // Debian Family - Using emojis (logo URLs unreliable)
  "Debian": {
    url: "",
    fallback: "🔴"
  },
  "Linux Mint": {
    url: "",
    fallback: "🍃"
  },
  "MX Linux": {
    url: "",
    fallback: "🐴"
  },
  "antiX": {
    url: "",
    fallback: "🐜"
  },

  // Fedora / Red Hat Family - Using emojis
  "Fedora": {
    url: "",
    fallback: "🔵"
  },
  "RHEL": {
    url: "",
    fallback: "🎩"
  },
  "Rocky Linux": {
    url: "",
    fallback: "💎"
  },
  "AlmaLinux": {
    url: "",
    fallback: "🐦"
  },
  "CentOS Stream": {
    url: "",
    fallback: "📦"
  },

  // Arch Linux Family - Using emojis
  "Arch Linux": {
    url: "",
    fallback: "🏔️"
  },
  "Manjaro": {
    url: "",
    fallback: "💚"
  },
  "EndeavourOS": {
    url: "",
    fallback: "🚀"
  },
  "Garuda Linux": {
    url: "",
    fallback: "🦅"
  },
  "Artix Linux": {
    url: "",
    fallback: "🎨"
  },
  "ArcoLinux": {
    url: "",
    fallback: "🎯"
  },

  // openSUSE Family
  "openSUSE": {
    url: "",
    fallback: "🦎"
  },

  // Independent Distributions - Using emojis
  "Pop!_OS": {
    url: "",
    fallback: "🚀"
  },
  "elementary OS": {
    url: "",
    fallback: "💎"
  },
  "Zorin OS": {
    url: "",
    fallback: "🌟"
  },
  "Solus": {
    url: "",
    fallback: "🌿"
  },
  "KDE neon": {
    url: "",
    fallback: "💠"
  },
  "NixOS": {
    url: "",
    fallback: "🌱"
  },
  "Gentoo": {
    url: "",
    fallback: "💜"
  },
  "Slackware": {
    url: "",
    fallback: "🔷"
  },
  "Void Linux": {
    url: "",
    fallback: "⚫"
  },
  "Deepin": {
    url: "",
    fallback: "🎨"
  },
  "Bodhi Linux": {
    url: "",
    fallback: "🌸"
  },
  "Q4OS": {
    url: "",
    fallback: "🔵"
  },
  "PCLinuxOS": {
    url: "",
    fallback: "🌲"
  },
  "BigLinux": {
    url: "",
    fallback: "🇧🇷"
  },
  "RebeccaBlackOS": {
    url: "",
    fallback: "🎬"
  },

  // Security Distributions - Using emojis
  "Kali Linux": {
    url: "",
    fallback: "🐉"
  },
  "Parrot OS": {
    url: "",
    fallback: "🦜"
  },
  "Tails": {
    url: "",
    fallback: "🕵️"
  },

  // Lightweight
  "Puppy Linux": {
    url: "",
    fallback: "🐕"
  },
};

/**
 * macOS Logos
 */
export const macOSLogos: Record<string, { url: string; fallback: string }> = {
  "macOS Sequoia": {
    url: "",
    fallback: "🍎"
  },
  "macOS Sonoma": {
    url: "",
    fallback: "🍏"
  },
  "macOS Ventura": {
    url: "",
    fallback: "🍐"
  },
  "macOS Monterey": {
    url: "",
    fallback: "🌊"
  },
  "macOS Big Sur": {
    url: "",
    fallback: "🏔️"
  },
  "macOS Catalina": {
    url: "",
    fallback: "🐱"
  },
  "macOS Mojave": {
    url: "",
    fallback: "🌵"
  },
  "macOS High Sierra": {
    url: "",
    fallback: "⛰️"
  },
};

/**
 * BSD Distribution Logos
 */
export const bsdLogos: Record<string, { url: string; fallback: string }> = {
  "FreeBSD": {
    url: "",
    fallback: "😈"
  },
  "OpenBSD": {
    url: "",
    fallback: "🐡"
  },
  "NetBSD": {
    url: "",
    fallback: "👻"
  },
  "GhostBSD": {
    url: "",
    fallback: "👻"
  },
  "OPNsense": {
    url: "",
    fallback: "🔥"
  },
  "pfSense": {
    url: "",
    fallback: "🔒"
  },
  "DragonFly BSD": {
    url: "",
    fallback: "🐉"
  },
  "DesktopBSD": {
    url: "",
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
