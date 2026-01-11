"""
Pydantic schemas for API request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Import enums from core to avoid duplication
from core.models import OSCategory, Architecture, DownloadState


# ========== OS Info Schemas ==========


class OSInfoResponse(BaseModel):
    """OS information response."""
    id: str
    name: str
    version: str
    category: str  # Changed from OSCategory enum to string for better compatibility
    architecture: Architecture
    language: str
    size: Optional[int] = None
    size_formatted: Optional[str] = None
    source: Optional[str] = None
    icon: Optional[str] = None
    url: str
    checksum: Optional[str] = None
    checksum_type: Optional[str] = None
    description: Optional[str] = None
    release_date: Optional[datetime] = None
    subcategory: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class OSCategoryResponse(BaseModel):
    """OS category with count."""
    category: OSCategory
    name: str
    icon: str
    count: int


class LinuxSubcategoryResponse(BaseModel):
    """Linux distribution subcategory with count."""
    subcategory: str
    name: str
    icon: str
    count: int


# ========== Download Request Schemas ==========


class StartDownloadRequest(BaseModel):
    """Request to start a download."""
    os_id: str = Field(..., description="ID of the OS to download")
    output_name: Optional[str] = Field(None, description="Custom output filename (without extension)")


class PauseDownloadRequest(BaseModel):
    """Request to pause/resume a download."""
    download_id: int = Field(..., description="ID of the download")


class CancelDownloadRequest(BaseModel):
    """Request to cancel a download."""
    download_id: int = Field(..., description="ID of the download")


# ========== Download Response Schemas ==========


class DownloadStatusResponse(BaseModel):
    """Download status response."""
    id: int
    os_name: str
    os_version: str
    os_category: str
    os_architecture: str
    os_icon: Optional[str] = None
    state: DownloadState
    progress: float = Field(..., ge=0, le=100, description="Progress percentage (0-100)")
    downloaded_bytes: int
    total_bytes: int
    downloaded_formatted: str
    total_formatted: str
    speed: float = 0.0
    speed_formatted: str
    eta: int = 0
    eta_formatted: str
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    checksum_verified: Optional[int] = None
    output_path: str

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class DownloadProgressUpdate(BaseModel):
    """Real-time download progress update (WebSocket)."""
    download_id: int
    state: DownloadState
    progress: float
    downloaded_bytes: int
    total_bytes: int
    speed: float
    eta: int
    error_message: Optional[str] = None


# ========== Settings Schemas ==========


class SettingValue(BaseModel):
    """Setting value."""
    key: str
    value: str


class SettingsResponse(BaseModel):
    """User settings response."""
    download_directory: str
    max_concurrent_downloads: int
    auto_start_downloads: bool
    theme: str


class UpdateSettingsRequest(BaseModel):
    """Request to update settings."""
    download_directory: Optional[str] = None
    max_concurrent_downloads: Optional[int] = Field(None, ge=1, le=10)
    auto_start_downloads: Optional[bool] = None
    theme: Optional[str] = Field(None, pattern="^(light|dark|auto)$")


# ========== Stats Schemas ==========


class StatsResponse(BaseModel):
    """Application statistics."""
    total_downloads: int
    active_downloads: int
    completed_downloads: int
    failed_downloads: int
    total_bytes_downloaded: int
    total_bytes_formatted: str
