"""
API routes for download management.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List

from api.database.session import get_db
from api.database.models import DownloadRecord, DownloadState
from api.models.schemas import (
    StartDownloadRequest,
    DownloadStatusResponse,
    StatsResponse,
)
from api.services.download import download_service
from api.routes import os as os_routes
from api.models.schemas import OSCategory, Architecture
from core.models import OSInfo, OSCategory as CoreOSCategory

router = APIRouter(prefix="/api/downloads", tags=["Downloads"])


@router.post("/start", response_model=DownloadStatusResponse)
async def start_download(
    request: StartDownloadRequest,
    db: Session = Depends(get_db),
) -> DownloadStatusResponse:
    """
    Start a new download.

    Args:
        request: Download request with OS ID
        db: Database session

    Returns:
        Download status
    """
    # Parse OS ID to get category and details
    # Format: category_name_version_architecture
    parts = request.os_id.split("_")
    if len(parts) < 4:
        raise HTTPException(status_code=400, detail="Invalid OS ID format")

    category_str = parts[0]
    try:
        category = OSCategory(category_str)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid category: {category_str}")

    # Get all OS for category and find matching one
    all_os = await os_routes.get_os_by_category(category)
    os_response = None
    for os_item in all_os:
        if os_item.id == request.os_id:
            os_response = os_item
            break

    if not os_response:
        raise HTTPException(status_code=404, detail="OS not found")

    # Convert to OSInfo model
    from core.models import Architecture as CoreArch
    arch_map = {
        Architecture.X64: CoreArch.X64,
        Architecture.X86: CoreArch.X86,
        Architecture.ARM64: CoreArch.ARM64,
        Architecture.ARM: CoreArch.ARM,
    }

    os_info = OSInfo(
        name=os_response.name,
        version=os_response.version,
        category=CoreOSCategory(os_response.category.value),
        architecture=arch_map.get(os_response.architecture, CoreArch.X64),
        language=os_response.language,
        url=os_response.url,
        checksum=os_response.checksum,
        checksum_type=os_response.checksum_type,
        size=os_response.size,
    )

    # Start download
    record = await download_service.start_download(os_info, db)

    return _record_to_response(record)


@router.get("/direct/{os_id}")
async def direct_download(os_id: str) -> RedirectResponse:
    """
    Direct download - redirects to the ISO URL so browser downloads it externally.

    This works like os.click - clicking download starts the ISO download directly
    from the source, not through the server.

    Args:
        os_id: OS ID (format: category_name_version_architecture)

    Returns:
        Redirect to the ISO URL
    """
    # Parse OS ID
    parts = os_id.split("_")
    if len(parts) < 4:
        raise HTTPException(status_code=400, detail="Invalid OS ID format")

    category_str = parts[0]
    try:
        category = OSCategory(category_str)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid category: {category_str}")

    # Get all OS for category and find matching one
    all_os = await os_routes.get_os_by_category(category)
    os_response = None
    for os_item in all_os:
        if os_item.id == os_id:
            os_response = os_item
            break

    if not os_response:
        raise HTTPException(status_code=404, detail="OS not found")

    # Redirect to the ISO URL directly
    # Browser will download from the source (like os.click)
    return RedirectResponse(url=os_response.url, status_code=302)


@router.get("", response_model=List[DownloadStatusResponse])
async def get_downloads(
    state: DownloadState | None = None,
    db: Session = Depends(get_db),
) -> List[DownloadStatusResponse]:
    """
    Get all downloads.

    Args:
        state: Filter by state (optional)
        db: Database session

    Returns:
        List of downloads
    """
    query = db.query(DownloadRecord)

    if state:
        query = query.filter(DownloadRecord.state == state)

    records = query.order_by(DownloadRecord.created_at.desc()).all()

    return [_record_to_response(record) for record in records]


@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: Session = Depends(get_db)) -> StatsResponse:
    """
    Get download statistics.

    Args:
        db: Database session

    Returns:
        Download statistics
    """
    total = db.query(DownloadRecord).count()

    active = (
        db.query(DownloadRecord)
        .filter(DownloadRecord.state == DownloadState.DOWNLOADING)
        .count()
    )

    completed = (
        db.query(DownloadRecord)
        .filter(DownloadRecord.state == DownloadState.COMPLETED)
        .count()
    )

    failed = (
        db.query(DownloadRecord)
        .filter(DownloadRecord.state == DownloadState.FAILED)
        .count()
    )

    # Calculate total bytes downloaded
    completed_records = (
        db.query(DownloadRecord)
        .filter(DownloadRecord.state == DownloadState.COMPLETED)
        .all()
    )

    total_bytes = sum(r.total_bytes for r in completed_records if r.total_bytes)

    return StatsResponse(
        total_downloads=total,
        active_downloads=active,
        completed_downloads=completed,
        failed_downloads=failed,
        total_bytes_downloaded=total_bytes,
        total_bytes_formatted=_format_bytes(total_bytes),
    )


@router.get("/{download_id}", response_model=DownloadStatusResponse)
async def get_download(
    download_id: int,
    db: Session = Depends(get_db),
) -> DownloadStatusResponse:
    """
    Get a specific download.

    Args:
        download_id: Download ID
        db: Database session

    Returns:
        Download status
    """
    record = (
        db.query(DownloadRecord)
        .filter(DownloadRecord.id == download_id)
        .first()
    )

    if not record:
        raise HTTPException(status_code=404, detail="Download not found")

    return _record_to_response(record)


@router.post("/{download_id}/pause")
async def pause_download(download_id: int) -> dict:
    """
    Pause a download.

    Args:
        download_id: Download ID

    Returns:
        Success message
    """
    success = await download_service.pause_download(download_id)

    if not success:
        raise HTTPException(status_code=400, detail="Could not pause download")

    return {"success": True, "message": "Download paused"}


@router.post("/{download_id}/resume")
async def resume_download(download_id: int) -> dict:
    """
    Resume a paused download.

    Args:
        download_id: Download ID

    Returns:
        Success message
    """
    success = await download_service.resume_download(download_id)

    if not success:
        raise HTTPException(status_code=400, detail="Could not resume download")

    return {"success": True, "message": "Download resumed"}


@router.delete("/completed")
async def clear_completed(db: Session = Depends(get_db)) -> dict:
    """
    Clear completed downloads.

    Args:
        db: Database session

    Returns:
        Success message with count
    """
    count = await download_service.clear_completed(db)

    return {"success": True, "message": f"Cleared {count} downloads"}


@router.post("/{download_id}/cancel")
async def cancel_download(download_id: int) -> dict:
    """
    Cancel a download (keeps it in database with cancelled state).

    Args:
        download_id: Download ID

    Returns:
        Success message
    """
    success = await download_service.cancel_download(download_id)

    return {"success": True, "message": "Download cancelled"}


@router.delete("/{download_id}")
async def delete_download(download_id: int, db: Session = Depends(get_db)) -> dict:
    """
    Delete a download from the database (dismiss button).

    Args:
        download_id: Download ID
        db: Database session

    Returns:
        Success message
    """
    # First cancel if active
    await download_service.cancel_download(download_id)

    # Then delete from database
    record = db.query(DownloadRecord).filter(DownloadRecord.id == download_id).first()
    if record:
        db.delete(record)
        db.commit()

    return {"success": True, "message": "Download deleted"}


def _record_to_response(record: DownloadRecord) -> DownloadStatusResponse:
    """Convert database record to response model."""
    # Get icon based on category
    icons = {
        "windows": "[_]".replace("[", "").replace("]", ""),
        "linux": "[+]".replace("[", "").replace("]", ""),
        "macos": "[/]".replace("[", "").replace("]", ""),
    }
    icon = icons.get(record.os_category, "[*]".replace("[", "").replace("]", ""))

    return DownloadStatusResponse(
        id=record.id,
        os_name=record.os_name,
        os_version=record.os_version,
        os_category=record.os_category,
        os_architecture=record.os_architecture,
        os_icon=icon,
        state=record.state,
        progress=record.progress or 0,
        downloaded_bytes=record.downloaded_bytes or 0,
        total_bytes=record.total_bytes or 0,
        downloaded_formatted=_format_bytes(record.downloaded_bytes or 0),
        total_formatted=_format_bytes(record.total_bytes or 0),
        speed=record.speed or 0,
        speed_formatted=_format_bytes(int(record.speed or 0)) + "/s",
        eta=record.eta or 0,
        eta_formatted=_format_duration(record.eta or 0),
        created_at=record.created_at,
        started_at=record.started_at,
        completed_at=record.completed_at,
        error_message=record.error_message,
        checksum_verified=record.checksum_verified,
        output_path=record.output_path,
    )


def _format_bytes(bytes: int) -> str:
    """Format bytes to human readable format."""
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(bytes)
    unit_index = 0

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    if unit_index == 0:
        return f"{bytes} {units[unit_index]}"
    return f"{size:.1f} {units[unit_index]}"


def _format_duration(seconds: int) -> str:
    """Format seconds to human readable duration."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins}m {secs}s"
    else:
        hours = seconds // 3600
        mins = (seconds % 3600) // 60
        return f"{hours}h {mins}m"
