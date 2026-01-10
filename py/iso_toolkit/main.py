"""
Main entry point for ISO Toolkit.

A beautiful multi-OS ISO downloader toolkit for Windows, Linux, macOS, and more.
"""

import sys
import subprocess
import importlib
from pathlib import Path
from typing import List, Tuple


# Required packages for the application
REQUIRED_PACKAGES = {
    "textual": "textual>=0.86.0",
    "requests": "requests>=2.31.0",
    "bs4": "beautifulsoup4>=4.12.0",
    "typing_extensions": "typing-extensions>=4.9.0",
    "toml": "toml>=0.10.2",
}

# Optional packages (not required for basic functionality)
OPTIONAL_PACKAGES = {
    "_core": "Rust extension (requires Rust toolchain)",
}


def check_and_install_dependencies() -> bool:
    """
    Check if all required dependencies are installed.
    If not, prompt the user to install them automatically.

    Returns:
        True if all dependencies are available, False otherwise.
    """
    missing_packages: List[Tuple[str, str]] = []
    optional_missing: List[Tuple[str, str]] = []

    # Check required packages
    for module_name, package_spec in REQUIRED_PACKAGES.items():
        try:
            importlib.import_module(module_name)
        except ImportError:
            missing_packages.append((module_name, package_spec))

    # Check optional packages
    for module_name, description in OPTIONAL_PACKAGES.items():
        try:
            importlib.import_module(module_name)
        except ImportError:
            optional_missing.append((module_name, description))

    # Install missing required packages
    if missing_packages:
        print("=" * 60)
        print("[bold yellow]ISO Toolkit - First Run Setup[/bold yellow]")
        print("=" * 60)
        print("\n[dim]The following required packages are missing:[/dim]")

        for module_name, package_spec in missing_packages:
            print(f"  - [red]{module_name}[/red] ({package_spec})")

        print("\n[bold cyan]Installing required dependencies...[/bold cyan]")

        packages_to_install = [spec for _, spec in missing_packages]

        try:
            # Use subprocess to install packages
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "--quiet"] + packages_to_install
            )
            print("[bold green][v] All required dependencies installed successfully![/bold green]\n")
        except subprocess.CalledProcessError as e:
            print(f"[bold red][x] Failed to install dependencies: {e}[/bold red]")
            print("\n[yellow]Please install manually:[/yellow]")
            print(f"  pip install {' '.join(packages_to_install)}")
            return False
    else:
        print("[dim][v] All required dependencies are installed.[/dim]")

    # Show optional packages info
    if optional_missing:
        print("\n[dim]Optional packages not installed:[/dim]")
        for module_name, description in optional_missing:
            print(f"  - {module_name} - {description}")

        # Special handling for Rust extension
        if any("_core" in m for m, _ in optional_missing):
            print("\n[yellow]Note: Rust extension provides faster downloads.[/yellow]")
            print("[dim]To install:[/dim]")
            print("  1. Install Rust: https://rustup.rs/")
            print("  2. Install maturin: pip install maturin")
            print("  3. Build extension: python -m maturin develop")
            print("\n[dim]The app will work with pure Python fallback.[/dim]")
            return "rust_missing"

    print()
    return True


def verify_installation() -> bool:
    """
    Verify that all imports work correctly.

    Returns:
        True if verification passes, False otherwise.
    """
    try:
        # Import all required modules
        import textual
        import requests
        import bs4
        import typing_extensions
        import toml

        # Try to import our app modules
        from iso_toolkit.models import OSCategory, OSInfo
        from iso_toolkit.manager import DownloadManager
        from iso_toolkit.os.base import get_registry
        from iso_toolkit.os.windows import WindowsProvider
        from iso_toolkit.os.linux import LinuxProvider
        from iso_toolkit.tui.app import ISOToolkitApp

        return True
    except ImportError as e:
        print(f"[red]Import error: {e}[/red]")
        return False


def main():
    """Main entry point for the application."""
    try:
        # Check and install dependencies on first run
        dep_status = check_and_install_dependencies()

        if not dep_status:
            print("\n[red]Cannot proceed without required dependencies.[/red]")
            sys.exit(1)

        # Verify installation
        if not verify_installation():
            print("\n[red]Installation verification failed.[/red]")
            print("[yellow]Please report this issue on GitHub.[/yellow]")
            sys.exit(1)

        # Check for Rust extension and show status (only if not already shown as missing)
        if dep_status != "rust_missing":
            has_rust = False
            try:
                from iso_toolkit import _core
                has_rust = True
                print("[bold green][v] Rust extension loaded - Fast downloads enabled![/bold green]\n")
            except ImportError:
                print("[dim]i Rust extension not found - Using Python fallback.[/dim]")
                print("[dim]  Downloads will still work but may be slower.[/dim]\n")

        # Set up and run the app
        from iso_toolkit.tui.app import ISOToolkitApp
        app = ISOToolkitApp()
        app.run()

    except KeyboardInterrupt:
        print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        print(f"[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
