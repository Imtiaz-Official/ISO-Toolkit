#!/bin/bash
# Download official Linux distribution logos

LOGO_DIR="$(dirname "$0")/logos"
mkdir -p "$LOGO_DIR"

# Ubuntu Family
curl -L -o "$LOGO_DIR/ubuntu.svg" "https://assets.ubuntu.com/v1/73a4d93d-ubuntu-cof-orange.svg"
curl -L -o "$LOGO_DIR/kubuntu.svg" "https://assets.ubuntu.com/v1/751d5a7d-kubuntu-logo-a-2022.svg"
curl -L -o "$LOGO_DIR/xubuntu.svg" "https://assets.ubuntu.com/v1/9aebfd65-xubuntu-logo-a.svg"
curl -L -o "$LOGO_DIR/lubuntu.svg" "https://assets.ubuntu.com/v1/e9a4d93d-lubuntu-logo-a.svg"
curl -L -o "$LOGO_DIR/ubuntu-mate.svg" "https://ubuntu-mate.org/static/logo.svg"
curl -L -o "$LOGO_DIR/ubuntu-studio.svg" "https://ubuntustudio.org/wp-content/uploads/2019/08/us-logo-white.svg"
curl -L -o "$LOGO_DIR/ubuntu-budgie.svg" "https://ubuntubudgie.org/wp-content/uploads/2021/08/budgie-logo.svg"
curl -L -o "$LOGO_DIR/ubuntu-cinnamon.svg" "https://ubuntucinnamon.org/static/logo.svg"

# Debian Family
curl -L -o "$LOGO_DIR/debian.svg" "https://www.debian.org/Pics/debian-logo.svg"
curl -L -o "$LOGO_DIR/linux-mint.svg" "https://linuxmint.com/favicon.ico"
curl -L -o "$LOGO_DIR/mx-linux.svg" "https://mxlinux.org/wp-content/uploads/mx-logo.svg"
curl -L -o "$LOGO_DIR/antix.svg" "https://antixlinux.com/wp-content/uploads/2022/09/antix-logo.svg"
curl -L -o "$LOGO_DIR/raspberry-pi-os.svg" "https://www.raspberrypi.com/favicon.ico"

# Fedora / Red Hat Family
curl -L -o "$LOGO_DIR/fedora.svg" "https://fedoraproject.org/static/images/fedora-logo.svg"
curl -L -o "$LOGO_DIR/fedora-workstation.svg" "https://fedoraproject.org/static/images/fedora-logo.svg"
curl -L -o "$LOGO_DIR/rhel.svg" "https://www.redhat.com/rhdc/managed-files/brand-assets/RHLogo_White_Black.svg"
curl -L -o "$LOGO_DIR/rocky-linux.svg" "https://rockylinux.org/img/logo-dark.svg"
curl -L -o "$LOGO_DIR/almalinux.svg" "https://almalinux.org/wp-content/uploads/2021/08/almalinux-logo-dark.svg"
curl -L -o "$LOGO_DIR/centos-stream.svg" "https://www.centos.org/assets/img/centos-logo.svg"
curl -L -o "$LOGO_DIR/oracle-linux.svg" "https://www.oracle.com/webfolder/s/brand-management/oracle-logo.svg"

# Arch Linux Family
curl -L -o "$LOGO_DIR/arch-linux.svg" "https://archlinux.org/static/logo.svg"
curl -L -o "$LOGO_DIR/manjaro.svg" "https://manjaro.org/static/logo.svg"
curl -L -o "$LOGO_DIR/endeavouros.svg" "https://endeavouros.com/wp-content/uploads/2021/09/endeavouros-logo.svg"
curl -L -o "$LOGO_DIR/garuda-linux.svg" "https://garudalinux.org/static/logo.svg"
curl -L -o "$LOGO_DIR/artix-linux.svg" "https://artixlinux.org/static/logo.svg"
curl -L -o "$LOGO_DIR/arcolinux.svg" "https://arcolinux.com/static/logo.svg"

# openSUSE Family
curl -L -o "$LOGO_DIR/opensuse.svg" "https://en.opensuse.org/images/0/0b/Logo-geeko_head.svg"
curl -L -o "$LOGO_DIR/opensuse-leap.svg" "https://en.opensuse.org/images/0/0b/Logo-geeko_head.svg"

# Independent Distributions
curl -L -o "$LOGO_DIR/pop-os.svg" "https://pop.system76.com/img/pop-logo.svg"
curl -L -o "$LOGO_DIR/elementary-os.svg" "https://elementary.io/images/elementaryos_logo.svg"
curl -L -o "$LOGO_DIR/zorin-os.svg" "https://zorinos.com/static/logo.svg"
curl -L -o "$LOGO_DIR/solus.svg" "https://getsol.us/images/logo.svg"
curl -L -o "$LOGO_DIR/kde-neon.svg" "https://kde.org/images/stable/kslogo.svg"
curl -L -o "$LOGO_DIR/nixos.svg" "https://nixos.org/logo/nixos-logo.svg"
curl -L -o "$LOGO_DIR/gentoo.svg" "https://www.gentoo.org/assets/img/logo/gentoo-logo.svg"
curl -L -o "$LOGO_DIR/slackware.svg" "https://www.slackware.com/logo.svg"
curl -L -o "$LOGO_DIR/void-linux.svg" "https://voidlinux.org/assets/logo.svg"
curl -L -o "$LOGO_DIR/deepin.svg" "https://www.deepin.org/en/logo.svg"
curl -L -o "$LOGO_DIR/bodhi-linux.svg" "https://bodhilinux.com/static/logo.svg"
curl -L -o "$LOGO_DIR/q4os.svg" "https://q4os.org/static/logo.svg"
curl -L -o "$LOGO_DIR/pclinuxos.svg" "https://pclinuxos.com/static/logo.svg"
curl -L -o "$LOGO_DIR/dietpi.svg" "https://dietpi.com/favicon.ico"
curl -L -o "$LOGO_DIR/libreelec.svg" "https://libreelec.com/favicon.ico"

# Security Distributions
curl -L -o "$LOGO_DIR/kali-linux.svg" "https://www.kali.org/images/kali-logo.svg"
curl -L -o "$LOGO_DIR/parrot-os.svg" "https://parrotsec.org/static/logo.svg"
curl -L -o "$LOGO_DIR/tails.svg" "https://tails.net/images/tails-logo.svg"

# Lightweight
curl -L -o "$LOGO_DIR/alpine-linux.svg" "https://alpinelinux.org/alpine-logo.svg"
curl -L -o "$LOGO_DIR/puppy-linux.svg" "https://puppylinux.com/static/logo.svg"

echo "All logos downloaded to $LOGO_DIR"
