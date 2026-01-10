"""
ISO Toolkit - A beautiful multi-OS ISO downloader toolkit

Supports downloading ISO images for Windows, Linux, macOS, BSD, and more.
"""

__version__ = "0.1.0"

try:
    from . import _core
except ImportError:
    _core = None

from iso_toolkit.models import OSInfo, OSCategory, DownloadState
from iso_toolkit.manager import DownloadManager

__all__ = [
    "OSInfo",
    "OSCategory",
    "DownloadState",
    "DownloadManager",
    "_core",
]
