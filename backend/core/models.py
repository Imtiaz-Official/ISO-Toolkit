"""
Data models for the ISO Toolkit application.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Callable, Any
from datetime import datetime


class OSCategory(str, Enum):
    """Operating system categories."""
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"
    BSD = "bsd"
    OTHER = "other"


class Architecture(str, Enum):
    """CPU architectures."""
    X64 = "x64"
    X86 = "x86"
    ARM64 = "arm64"
    ARM = "arm"
    RISCV64 = "riscv64"
    UNIVERSAL = "universal"


class DownloadState(Enum):
    """States of a download."""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFYING = "verifying"
    CANCELLED = "cancelled"


@dataclass
class OSInfo:
    """
    Information about an available OS ISO.
    """
    name: str  # e.g., "Windows 11", "Ubuntu Desktop"
    version: str  # e.g., "23H2", "24.04 LTS"
    category: OSCategory
    architecture: Architecture
    language: str  # e.g., "en-US", "Multi"
    url: str
    checksum: Optional[str] = None
    checksum_type: Optional[str] = None  # "sha256", "md5"
    size: Optional[int] = None  # in bytes
    release_date: Optional[datetime] = None
    description: Optional[str] = None
    icon: Optional[str] = None  # emoji or icon identifier
    source: Optional[str] = None  # e.g., "Microsoft", "Ubuntu", "Internet Archive"
    subcategory: Optional[str] = None  # e.g., "Ubuntu", "Fedora" for Linux distros

    @property
    def display_name(self) -> str:
        """Human readable display name."""
        return f"{self.name} {self.version}"

    @property
    def size_formatted(self) -> str:
        """Human readable size."""
        if self.size is None:
            return "Unknown"
        return self._format_bytes(self.size)

    @staticmethod
    def _format_bytes(bytes: int) -> str:
        units = ["B", "KB", "MB", "GB", "TB"]
        size = float(bytes)
        unit_index = 0

        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1

        if unit_index == 0:
            return f"{bytes} {units[unit_index]}"
        return f"{size:.1f} {units[unit_index]}"


@dataclass
class DownloadProgress:
    """Progress information for an active download."""
    downloaded: int
    total: int
    speed: float  # bytes per second
    eta: int  # seconds remaining

    @property
    def percentage(self) -> float:
        """Progress as percentage."""
        if self.total == 0:
            return 0.0
        return (self.downloaded / self.total) * 100

    @property
    def downloaded_formatted(self) -> str:
        """Human readable downloaded amount."""
        return OSInfo._format_bytes(self.downloaded)

    @property
    def total_formatted(self) -> str:
        """Human readable total size."""
        return OSInfo._format_bytes(self.total)

    @property
    def speed_formatted(self) -> str:
        """Human readable speed."""
        return OSInfo._format_bytes(int(self.speed)) + "/s"

    @property
    def eta_formatted(self) -> str:
        """Human readable ETA."""
        if self.eta < 60:
            return f"{self.eta}s"
        elif self.eta < 3600:
            mins = self.eta // 60
            secs = self.eta % 60
            return f"{mins}m {secs}s"
        else:
            hours = self.eta // 3600
            mins = (self.eta % 3600) // 60
            return f"{hours}h {mins}m"


@dataclass
class DownloadTask:
    """A download task with its current state."""
    os_info: OSInfo
    output_path: str
    state: DownloadState = DownloadState.PENDING
    progress: Optional[DownloadProgress] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    on_progress: Optional[Callable[[DownloadProgress], Any]] = None
    on_state_change: Optional[Callable[[DownloadState], Any]] = None
    on_complete: Optional[Callable[[bool, Optional[str]], Any]] = None

    # Internal state
    _callback_handle: Optional[Callable[[int, int], bool]] = field(default=None, repr=False)
    _cancelled: bool = field(default=False, repr=False)

    def cancel(self) -> None:
        """Cancel this download task."""
        self._cancelled = True
        self.state = DownloadState.CANCELLED

    def is_cancelled(self) -> bool:
        """Check if this download was cancelled."""
        return self._cancelled


@dataclass
class ProviderConfig:
    """Configuration for an ISO provider."""
    name: str
    base_url: str
    enabled: bool = True
    requires_auth: bool = False
    rate_limit: Optional[int] = None  # requests per minute
