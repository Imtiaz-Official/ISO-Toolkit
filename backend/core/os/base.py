"""
Base classes for OS providers.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from core.models import OSInfo, OSCategory, Architecture


@dataclass
class ProviderMetadata:
    """Metadata about a provider."""
    name: str
    category: OSCategory
    description: str
    icon: str
    version: str = "0.1.0"
    enabled: bool = True


class BaseProvider(ABC):
    """
    Abstract base class for OS ISO providers.

    Providers are responsible for fetching available ISO information
    from various sources (official websites, archives, APIs).
    """

    def __init__(self):
        self._cache: Dict[str, List[OSInfo]] = {}

    @property
    @abstractmethod
    def metadata(self) -> ProviderMetadata:
        """Get provider metadata."""
        pass

    @abstractmethod
    async def fetch_available(self, **filters) -> List[OSInfo]:
        """
        Fetch available ISOs from the provider.

        Args:
            **filters: Optional filters like architecture, language, version

        Returns:
            List of OSInfo objects
        """
        pass

    @abstractmethod
    def get_supported_architectures(self) -> List[Architecture]:
        """Get list of supported architectures."""
        pass

    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """Get list of supported language codes."""
        pass

    def get_cached(self, cache_key: str) -> Optional[List[OSInfo]]:
        """Get cached results for a key."""
        return self._cache.get(cache_key)

    def set_cached(self, cache_key: str, data: List[OSInfo]) -> None:
        """Cache results for a key."""
        self._cache[cache_key] = data

    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear()


class ProviderRegistry:
    """
    Registry for all OS providers.

    Allows dynamic registration and lookup of providers by category.
    """

    def __init__(self):
        self._providers: Dict[OSCategory, List[BaseProvider]] = {}
        self._providers_map: Dict[str, BaseProvider] = {}

    def register(self, provider: BaseProvider) -> None:
        """Register a provider."""
        category = provider.metadata.category
        if category not in self._providers:
            self._providers[category] = []
        self._providers[category].append(provider)
        self._providers_map[provider.metadata.name.lower()] = provider

    def unregister(self, provider_name: str) -> None:
        """Unregister a provider by name."""
        provider = self._providers_map.pop(provider_name.lower(), None)
        if provider:
            category = provider.metadata.category
            if category in self._providers:
                self._providers[category] = [
                    p for p in self._providers[category]
                    if p.metadata.name.lower() != provider_name.lower()
                ]

    def get_by_category(self, category: OSCategory) -> List[BaseProvider]:
        """Get all providers for a category."""
        return self._providers.get(category, [])

    def get_by_name(self, name: str) -> Optional[BaseProvider]:
        """Get a provider by name."""
        return self._providers_map.get(name.lower())

    def get_all_categories(self) -> List[OSCategory]:
        """Get all registered categories."""
        return list(self._providers.keys())

    def get_all_providers(self) -> List[BaseProvider]:
        """Get all registered providers."""
        result = []
        for providers in self._providers.values():
            result.extend(providers)
        return result


# Global registry instance
_registry = ProviderRegistry()


def get_registry() -> ProviderRegistry:
    """Get the global provider registry."""
    return _registry


def register_provider(provider: BaseProvider) -> None:
    """Register a provider with the global registry."""
    _registry.register(provider)


def get_providers(category: OSCategory) -> List[BaseProvider]:
    """Get providers for a category from the global registry."""
    return _registry.get_by_category(category)
