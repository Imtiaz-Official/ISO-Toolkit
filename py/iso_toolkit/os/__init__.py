"""
OS provider modules - scrapers and data sources for different operating systems.
"""

from iso_toolkit.os.base import BaseProvider, ProviderRegistry
from iso_toolkit.os.windows import WindowsProvider
from iso_toolkit.os.linux import LinuxProvider
from iso_toolkit.os.macos import MacOSProvider

__all__ = [
    "BaseProvider",
    "ProviderRegistry",
    "WindowsProvider",
    "LinuxProvider",
    "MacOSProvider",
]
