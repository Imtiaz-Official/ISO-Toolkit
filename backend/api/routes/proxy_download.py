"""
Proxy download routes - Stream downloads through our server.
This makes all downloads appear to come from our domain.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
import httpx
import asyncio
from urllib.parse import urljoin

from api.database.session import get_db
from api.database.models import DownloadRecord
from core.models import DownloadState

router = APIRouter(prefix="/download", tags=["Proxy Downloads"])


# Chunk size for streaming downloads
CHUNK_SIZE = 1024 * 1024  # 1MB chunks
# Timeout for download requests
DOWNLOAD_TIMEOUT = 300  # 5 minutes


@router.get("/id/{os_id}")
async def proxy_download_by_id(
    os_id: str,
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Proxy download by OS ID.
    The OS ID is in format: category_name_version_architecture (e.g., windows_windows_11_24h2_x64)
    This is the most reliable way to proxy downloads.

    Supports resume/partial downloads via Range requests.
    Returns 206 Partial Content for Range requests to enable IDM resume.
    """
    from api.routes import os as os_routes
    from api.models.schemas import OSCategory

    # Parse OS ID to get category
    # Format: category_name_version_architecture
    parts = os_id.split("_")
    if len(parts) < 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OS ID format"
        )

    category_str = parts[0]
    try:
        category = OSCategory(category_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category: {category_str}"
        )

    # Get all OS for category and find matching one by ID
    all_os = await os_routes.get_os_by_category(category)
    matching_os = None
    for os_item in all_os:
        if os_item.id == os_id:
            matching_os = os_item
            break

    if not matching_os:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"OS not found: {os_id}"
        )

    # Generate filename
    ext = ".iso" if not matching_os.url.endswith(".ipsw") and not matching_os.url.endswith(".dmg") else ""
    filename = f"{matching_os.name} {matching_os.version}{ext}".replace(" ", "_")

    # Get custom headers from OS info if available
    headers = getattr(matching_os, "headers", {})

    # Check for Range request (for resume support)
    range_header = request.headers.get("range") if request else None

    # Determine if this is a range request for resume
    is_range_request = range_header is not None

    async def generate():
        """Stream the download in chunks with range support."""
        async with httpx.AsyncClient(timeout=DOWNLOAD_TIMEOUT) as client:
            try:
                # Forward Range header if present for resume support
                req_headers = headers.copy()
                if range_header:
                    req_headers["Range"] = range_header

                async with client.stream(
                    "GET",
                    matching_os.url,
                    headers=req_headers,
                    follow_redirects=True
                ) as response:
                    response.raise_for_status()

                    # Return response status code info for proper Range handling
                    if is_range_request and response.status_code == 206:
                        # Source returned 206 Partial Content - stream the partial content
                        async for chunk in response.aiter_bytes(chunk_size=CHUNK_SIZE):
                            yield chunk
                    else:
                        # Full content request
                        async for chunk in response.aiter_bytes(chunk_size=CHUNK_SIZE):
                            yield chunk

            except httpx.HTTPError as e:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Failed to fetch from source: {str(e)}"
                )

    # Build response headers with resume support
    response_headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Cache-Control": "public, max-age=31536000",
        "Accept-Ranges": "bytes",  # Enable resume support
        "X-Original-URL": matching_os.url,
    }

    # For Range requests, return 206 status code for IDM to recognize resume
    if range_header:
        return StreamingResponse(
            generate(),
            status_code=206,
            media_type="application/octet-stream",
            headers=response_headers
        )

    return StreamingResponse(
        generate(),
        media_type="application/octet-stream",
        headers=response_headers
    )


@router.get("/{download_id}")
async def proxy_download(
    download_id: int,
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Proxy a download through our server by database download record ID.

    The URL will be: /download/{id} instead of the original external URL.
    This makes all downloads appear to come from our domain.
    Supports resume/partial downloads via Range requests.
    """
    # Get the download record
    record = db.query(DownloadRecord).filter(DownloadRecord.id == download_id).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Download not found"
        )

    # Get the original URL
    original_url = record.url

    if not original_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No download URL available"
        )

    # Determine filename from output path or URL
    filename = record.output_path.split("/")[-1] if record.output_path else "download.iso"

    # Get custom headers if available (for some sources that need specific User-Agent)
    headers = {}

    # Check for Range request (for resume support)
    range_header = request.headers.get("range") if request else None

    async def generate():
        """Stream the download in chunks with range support."""
        async with httpx.AsyncClient(timeout=DOWNLOAD_TIMEOUT) as client:
            try:
                # Forward Range header if present for resume support
                req_headers = headers.copy()
                if range_header:
                    req_headers["Range"] = range_header

                async with client.stream("GET", original_url, headers=req_headers, follow_redirects=True) as response:
                    response.raise_for_status()

                    # Stream content in chunks
                    async for chunk in response.aiter_bytes(chunk_size=CHUNK_SIZE):
                        yield chunk

            except httpx.HTTPError as e:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Failed to fetch from source: {str(e)}"
                )

    # Build response headers with resume support
    response_headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Cache-Control": "no-cache",
        "Accept-Ranges": "bytes",  # Enable resume support
    }

    # For Range requests, return 206 status code for IDM to recognize resume
    if range_header:
        return StreamingResponse(
            generate(),
            status_code=206,
            media_type="application/octet-stream",
            headers=response_headers
        )

    return StreamingResponse(
        generate(),
        media_type="application/octet-stream",
        headers=response_headers
    )


@router.get("/direct/{os_category}/{os_name}")
async def direct_download(
    os_category: str,
    os_name: str,
    version: Optional[str] = None,
    architecture: Optional[str] = None,
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Direct download URL by OS info.
    Creates a URL like: /download/direct/linux/ubuntu or /download/direct/macos/ventura

    This will find the matching OS entry and proxy the download.
    Supports resume/partial downloads via Range requests.
    """
    from core.os.base import get_registry
    from core.models import OSCategory, Architecture

    # Parse category
    try:
        category = OSCategory(os_category.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid OS category: {os_category}"
        )

    # Get OS from registry
    registry = get_registry()
    providers = registry.get_by_category(category)

    matching_os = None
    for provider in providers:
        try:
            os_list = await provider.fetch_available()
            for os_info in os_list:
                # Match by name and optionally version/architecture
                if os_info.name.lower() == os_name.lower():
                    if version is None or os_info.version == version:
                        if architecture is None or os_info.architecture.value == architecture.lower():
                            matching_os = os_info
                            break
            if matching_os:
                break
        except Exception:
            continue

    if not matching_os:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"OS not found: {os_category}/{os_name}"
        )

    # Generate filename
    ext = ".iso" if not matching_os.url.endswith(".ipsw") and not matching_os.url.endswith(".dmg") else ""
    filename = f"{matching_os.name} {matching_os.version}{ext}".replace(" ", "_")

    # Get custom headers from OS info if available
    headers = getattr(matching_os, "headers", {})

    # Check for Range request (for resume support)
    range_header = request.headers.get("range") if request else None

    async def generate():
        """Stream the download in chunks with range support."""
        async with httpx.AsyncClient(timeout=DOWNLOAD_TIMEOUT) as client:
            try:
                # Forward Range header if present for resume support
                req_headers = headers.copy()
                if range_header:
                    req_headers["Range"] = range_header

                async with client.stream(
                    "GET",
                    matching_os.url,
                    headers=req_headers,
                    follow_redirects=True
                ) as response:
                    response.raise_for_status()

                    # Stream content in chunks
                    async for chunk in response.aiter_bytes(chunk_size=CHUNK_SIZE):
                        yield chunk

            except httpx.HTTPError as e:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Failed to fetch from source: {str(e)}"
                )

    # Build response headers with resume support
    response_headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Cache-Control": "public, max-age=31536000",
        "Accept-Ranges": "bytes",  # Enable resume support
        "X-Original-URL": matching_os.url,
    }

    # For Range requests, return 206 status code for IDM to recognize resume
    if range_header:
        return StreamingResponse(
            generate(),
            status_code=206,
            media_type="application/octet-stream",
            headers=response_headers
        )

    return StreamingResponse(
        generate(),
        media_type="application/octet-stream",
        headers=response_headers
    )


@router.get("/url/{encoded_url}")
async def proxy_download_by_url(
    encoded_url: str,
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Proxy download by base64 encoded URL.
    This allows any URL to be proxied through our server.
    Supports resume/partial downloads via Range requests.

    Usage: /download/url/{base64_encoded_url}
    Example: /download/url/aHR0cHM6Ly9leGFtcGxlLmNvbS9maWxlLmlzbw==
    """
    import base64

    try:
        # Decode the URL
        original_url = base64.urlsafe_b64decode(encoded_url).decode('utf-8')
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid encoded URL"
        )

    # Extract filename from URL
    from urllib.parse import urlparse
    parsed = urlparse(original_url)
    filename = parsed.path.split("/")[-1] or "download.iso"

    # Check for Range request (for resume support)
    range_header = request.headers.get("range") if request else None

    async def generate():
        """Stream the download in chunks with range support."""
        async with httpx.AsyncClient(timeout=DOWNLOAD_TIMEOUT) as client:
            try:
                # Forward Range header if present for resume support
                req_headers = {}
                if range_header:
                    req_headers["Range"] = range_header

                async with client.stream(
                    "GET",
                    original_url,
                    headers=req_headers,
                    follow_redirects=True
                ) as response:
                    response.raise_for_status()

                    # Stream content in chunks
                    async for chunk in response.aiter_bytes(chunk_size=CHUNK_SIZE):
                        yield chunk

            except httpx.HTTPError as e:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Failed to fetch from source: {str(e)}"
                )

    # Build response headers with resume support
    response_headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Cache-Control": "no-cache",
        "Accept-Ranges": "bytes",  # Enable resume support
        "X-Original-URL": original_url,
    }

    # For Range requests, return 206 status code for IDM to recognize resume
    if range_header:
        return StreamingResponse(
            generate(),
            status_code=206,
            media_type="application/octet-stream",
            headers=response_headers
        )

    return StreamingResponse(
        generate(),
        media_type="application/octet-stream",
        headers=response_headers
    )
