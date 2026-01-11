"""
Proxy download routes - Stream downloads through our server.
This makes all downloads appear to come from our domain.
"""

from fastapi import APIRouter, Depends, HTTPException, status
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


@router.get("/{download_id}")
async def proxy_download(
    download_id: int,
    db: Session = Depends(get_db)
):
    """
    Proxy a download through our server.

    The URL will be: /download/{id} instead of the original external URL.
    This makes all downloads appear to come from our domain.
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
    # We'll need to store headers in the database or fetch from OS info
    # For now, use a standard user agent

    async def generate():
        """Stream the download in chunks."""
        async with httpx.AsyncClient(timeout=DOWNLOAD_TIMEOUT) as client:
            try:
                async with client.stream("GET", original_url, headers=headers, follow_redirects=True) as response:
                    response.raise_for_status()

                    # Stream content in chunks
                    async for chunk in response.aiter_bytes(chunk_size=CHUNK_SIZE):
                        yield chunk

            except httpx.HTTPError as e:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Failed to fetch from source: {str(e)}"
                )

    # Return streaming response with proper headers
    return StreamingResponse(
        generate(),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache",
        }
    )


@router.get("/direct/{os_category}/{os_name}")
async def direct_download(
    os_category: str,
    os_name: str,
    version: Optional[str] = None,
    architecture: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Direct download URL by OS info.
    Creates a URL like: /download/direct/linux/ubuntu or /download/direct/macos/ventura

    This will find the matching OS entry and proxy the download.
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

    async def generate():
        """Stream the download in chunks."""
        async with httpx.AsyncClient(timeout=DOWNLOAD_TIMEOUT) as client:
            try:
                async with client.stream(
                    "GET",
                    matching_os.url,
                    headers=headers,
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

    # Return streaming response
    return StreamingResponse(
        generate(),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "public, max-age=31536000",  # Cache for 1 year
            "X-Original-URL": matching_os.url,
        }
    )


@router.get("/url/{encoded_url}")
async def proxy_download_by_url(encoded_url: str, db: Session = Depends(get_db)):
    """
    Proxy download by base64 encoded URL.
    This allows any URL to be proxied through our server.

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

    async def generate():
        """Stream the download in chunks."""
        async with httpx.AsyncClient(timeout=DOWNLOAD_TIMEOUT) as client:
            try:
                async with client.stream(
                    "GET",
                    original_url,
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

    # Return streaming response
    return StreamingResponse(
        generate(),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache",
            "X-Original-URL": original_url,
        }
    )
