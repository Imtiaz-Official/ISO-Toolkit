"""
macOS OS provider - placeholder for future macOS support.

Note: macOS downloads are restricted by Apple's terms of service.
This module is a placeholder for potential future implementations.
"""

from typing import List
from datetime import datetime

from iso_toolkit.os.base import BaseProvider, ProviderMetadata
from iso_toolkit.models import OSInfo, OSCategory, Architecture


class MacOSProvider(BaseProvider):
    """
    Placeholder provider for macOS ISO downloads.

    Note: Official macOS downloads require Apple ID authentication
    and are only available from Apple's servers. This provider
    is not currently functional but serves as a placeholder for
    potential future implementations.
    """

    @property
    def metadata(self) -> ProviderMetadata:
        return ProviderMetadata(
            name="macOS",
            category=OSCategory.MACOS,
            description="Apple macOS (Not currently available)",
            icon="🍎",
            enabled=False,  # Disabled due to restrictions
        )

    def get_supported_architectures(self) -> List[Architecture]:
        return [Architecture.X64, Architecture.ARM64]

    def get_supported_languages(self) -> List[str]:
        return ["Multi"]

    async def fetch_available(self, **filters) -> List[OSInfo]:
        """
        macOS downloads are not currently supported.

        Official macOS downloads require:
        - Apple ID authentication
        - Access to Apple's developer portal or App Store

        This method returns an empty list.
        """
        return []

    async def _fetch_macos(self, **filters) -> List[OSInfo]:
        """Placeholder for macOS ISO fetching."""
        return []
