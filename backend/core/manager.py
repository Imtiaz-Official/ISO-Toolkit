"""
Download manager for handling ISO downloads with resume support, mirrors, and robust error handling.
"""

import os
import time
import threading
import hashlib
import ssl
import urllib3
import logging
from pathlib import Path
from typing import Optional, List
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from core.models import (
    DownloadTask,
    DownloadState,
    DownloadProgress,
    OSInfo,
)

logger = logging.getLogger(__name__)


def _has_rust_extension() -> bool:
    """Check if Rust extension is available."""
    try:
        from core import _core
        return True
    except ImportError:
        return False


HAS_RUST = _has_rust_extension()


def _create_download_session() -> requests.Session:
    """
    Create a requests session with proper SSL configuration and retry logic.
    """
    session = requests.Session()

    # Disable SSL warnings for self-signed certs (some archives use them)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Configure retry strategy - expanded to handle more cases
    retry_strategy = Retry(
        total=8,  # Increased from 5
        backoff_factor=2,
        status_forcelist=[403, 408, 429, 500, 502, 503, 504],  # Added 403, 408
        allowed_methods=["HEAD", "GET", "OPTIONS"],
        raise_on_status=False  # Don't raise immediately, handle errors manually
    )

    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=15,  # Increased from 10
        pool_maxsize=15
    )
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    # Default headers for all requests
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    })

    return session


# Global session for downloads
_download_session = _create_download_session()


class DownloadManager:
    """
    Manages ISO downloads with resume support, progress tracking, checksum verification,
    mirror support, and robust error handling.
    """

    def __init__(self, download_dir: Optional[str] = None):
        """
        Initialize the download manager.

        Args:
            download_dir: Default directory for downloads (default: ~/Downloads/ISOs)
        """
        if download_dir is None:
            download_dir = str(Path.home() / "Downloads" / "ISOs")

        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)

        self._active_tasks: List[DownloadTask] = []
        self._completed_tasks: List[DownloadTask] = []

    @property
    def active_tasks(self) -> List[DownloadTask]:
        """Get all active (not completed) download tasks."""
        return [t for t in self._active_tasks if t.state not in
                (DownloadState.COMPLETED, DownloadState.FAILED, DownloadState.CANCELLED)]

    @property
    def completed_tasks(self) -> List[DownloadTask]:
        """Get all completed download tasks."""
        return self._completed_tasks.copy()

    def get_output_path(self, os_info: OSInfo) -> str:
        """
        Generate output filename for an OS ISO.

        Format: {category}-{name}-{version}-{arch}-{lang}.{ext}
        Example: windows-windows-11-23h2-x64-en-us.iso
        """
        ext = "iso"
        category = os_info.category.value
        # Clean name for filename
        name_clean = os_info.name.lower().replace(" ", "-")
        version_clean = os_info.version.lower().replace(" ", "-").replace(".", "-")
        arch = os_info.architecture.value
        lang = os_info.language.lower().replace("-", "")

        filename = f"{category}-{name_clean}-{version_clean}-{arch}-{lang}.{ext}"
        return str(self.download_dir / filename)

    def create_download_task(self, os_info: OSInfo, output_path: Optional[str] = None) -> DownloadTask:
        """
        Create a new download task.

        Args:
            os_info: Information about the OS to download
            output_path: Custom output path (default: auto-generated)

        Returns:
            A new DownloadTask
        """
        if output_path is None:
            output_path = self.get_output_path(os_info)

        task = DownloadTask(
            os_info=os_info,
            output_path=output_path,
            state=DownloadState.PENDING,
        )

        self._active_tasks.append(task)
        return task

    def start_download(self, task: DownloadTask) -> bool:
        """
        Start a download task.

        Args:
            task: The download task to start

        Returns:
            True if download started successfully, False otherwise
        """
        if task.is_cancelled():
            return False

        # Check if file exists for resume
        resume = False
        if Path(task.output_path).exists():
            # Check if we can resume by comparing file size
            file_size = Path(task.output_path).stat().st_size
            if task.os_info.size and file_size < task.os_info.size:
                resume = True
                logger.info(f"Resuming download from {self._format_bytes(file_size)}")
            elif task.os_info.size and file_size >= task.os_info.size:
                # File already complete, just verify
                task.state = DownloadState.COMPLETED
                self._verify_and_complete(task)
                return True

        # Update state
        task.state = DownloadState.DOWNLOADING
        task.started_at = datetime.now()

        # Start download in background thread
        thread = threading.Thread(
            target=self._download_worker,
            args=(task, resume),
            daemon=True
        )
        thread.start()

        return True

    def _download_worker(self, task: DownloadTask, resume: bool) -> None:
        """Worker thread that handles the actual download with mirror support."""
        last_error = None

        try:
            # Try main URL first, then mirrors
            urls_to_try = [task.os_info.url] + task.os_info.mirrors

            for i, url in enumerate(urls_to_try):
                if task.is_cancelled():
                    return

                logger.info(f"Attempting download from source {i+1}/{len(urls_to_try)}: {url}")

                try:
                    if HAS_RUST:
                        self._download_with_rust(task, resume, url)
                    else:
                        self._download_with_python(task, resume, url)

                    # If successful, return
                    if task.state == DownloadState.COMPLETED:
                        logger.info(f"Download completed from source {i+1}")
                        return

                except Exception as e:
                    last_error = e
                    logger.warning(f"Download failed from source {i+1}: {e}")

                    # If not the last source, continue to next mirror
                    if i < len(urls_to_try) - 1:
                        logger.info(f"Trying next mirror...")
                        time.sleep(1)  # Brief pause before trying next mirror
                        continue

            # All sources failed
            if task.state not in (DownloadState.COMPLETED, DownloadState.CANCELLED):
                task.state = DownloadState.FAILED
                task.error_message = f"All download sources failed. Last error: {last_error}"
                logger.error(f"Download failed completely: {task.error_message}")
                if task.on_complete:
                    task.on_complete(False, task.error_message)

        finally:
            if task.state in (DownloadState.COMPLETED, DownloadState.FAILED, DownloadState.CANCELLED):
                if task not in self._completed_tasks:
                    self._completed_tasks.append(task)

    def _download_with_rust(self, task: DownloadTask, resume: bool, url: str) -> None:
        """Download using Rust extension (faster)."""
        from core import _core

        def progress_callback(downloaded: int, total: int) -> bool:
            if task.is_cancelled():
                return False

            self._update_task_progress(task, downloaded, total)
            return True

        result = _core.download_file(
            url,
            task.output_path,
            resume,
            progress_callback
        )

        if task.is_cancelled():
            task.state = DownloadState.CANCELLED
            return

        if result.success:
            task.state = DownloadState.VERIFYING
            self._verify_and_complete(task)
        else:
            task.state = DownloadState.FAILED
            task.error_message = result.error_message or "Download failed"
            raise Exception(task.error_message)

    def _download_with_python(self, task: DownloadTask, resume: bool, url: str) -> None:
        """Download using pure Python with robust error handling."""
        path = Path(task.output_path)
        start_pos = 0

        # Check for resume
        if resume and path.exists():
            start_pos = path.stat().st_size

        headers = {}
        if start_pos > 0:
            headers["Range"] = f"bytes={start_pos}-"

        # Add custom headers from OSInfo if available
        if task.os_info.headers:
            headers.update(task.os_info.headers)

        # Try with SSL verification first
        try:
            response = self._make_request(url, headers, verify_ssl=True, timeout=30)
        except (requests.exceptions.SSLError, requests.exceptions.RequestException) as e:
            logger.warning(f"Request with SSL failed: {e}, trying without SSL...")
            response = self._make_request(url, headers, verify_ssl=False, timeout=30)

        if response.status_code not in (200, 206):
            error_msg = f"HTTP error: {response.status_code} for {url}"
            logger.error(error_msg)
            task.state = DownloadState.FAILED
            task.error_message = error_msg
            if task.on_complete:
                task.on_complete(False, task.error_message)
            raise Exception(error_msg)

        # Get total size
        total_size = start_pos
        if "content-length" in response.headers:
            total_size += int(response.headers["content-length"])
        elif task.os_info.size:
            total_size = task.os_info.size

        mode = "ab" if resume and start_pos > 0 else "wb"

        downloaded = start_pos
        chunk_size = 65536  # Increased from 8192 for better performance
        last_progress_time = time.time()

        try:
            with open(path, mode) as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if task.is_cancelled():
                        task.state = DownloadState.CANCELLED
                        return

                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        # Update progress throttling (not every chunk)
                        current_time = time.time()
                        if current_time - last_progress_time >= 0.5:  # Every 0.5 seconds
                            self._update_task_progress(task, downloaded, total_size)
                            last_progress_time = current_time

        except IOError as e:
            task.state = DownloadState.FAILED
            task.error_message = f"File write error: {e}"
            logger.error(task.error_message)
            raise

        if not task.is_cancelled():
            # Final progress update
            self._update_task_progress(task, downloaded, total_size)
            task.state = DownloadState.VERIFYING
            self._verify_and_complete(task)

    def _make_request(self, url: str, headers: dict, verify_ssl: bool, timeout: int) -> requests.Response:
        """
        Make HTTP request with proper error handling.

        Args:
            url: The URL to request
            headers: Request headers
            verify_ssl: Whether to verify SSL certificates
            timeout: Request timeout in seconds

        Returns:
            Response object

        Raises:
            requests.RequestException: If request fails
        """
        return _download_session.get(
            url,
            headers=headers,
            stream=True,
            timeout=timeout,
            verify=verify_ssl
        )

    def _update_task_progress(self, task: DownloadTask, downloaded: int, total: int) -> None:
        """Update task progress and trigger callbacks."""
        if task.started_at:
            elapsed = (datetime.now() - task.started_at).total_seconds()
            if elapsed > 0:
                speed = downloaded / elapsed
                if speed > 0:
                    eta = int((total - downloaded) / speed)
                else:
                    eta = 0
            else:
                speed = 0
                eta = 0
        else:
            speed = 0
            eta = 0

        task.progress = DownloadProgress(
            downloaded=downloaded,
            total=total,
            speed=speed,
            eta=eta
        )

        if task.on_progress:
            try:
                task.on_progress(task.progress)
            except Exception as e:
                logger.warning(f"Progress callback error: {e}")

    def _verify_and_complete(self, task: DownloadTask) -> None:
        """Verify checksum and mark task as complete."""
        try:
            # Only verify if we have a valid checksum (not placeholder zeros)
            if (task.os_info.checksum and task.os_info.checksum_type and
                not task.os_info.checksum.startswith("00000000")):

                task.state = DownloadState.VERIFYING

                if HAS_RUST:
                    from core import _core
                    valid = _core.verify_checksum(
                        task.output_path,
                        task.os_info.checksum,
                        task.os_info.checksum_type
                    )
                else:
                    valid = self._verify_checksum_python(
                        task.output_path,
                        task.os_info.checksum,
                        task.os_info.checksum_type
                    )

                if not valid:
                    task.state = DownloadState.FAILED
                    task.error_message = f"Checksum verification failed"
                    logger.error(task.error_message)
                    if task.on_complete:
                        task.on_complete(False, task.error_message)
                    return
            else:
                logger.info("No valid checksum available, skipping verification")

            task.state = DownloadState.COMPLETED
            task.completed_at = datetime.now()

            actual_size = Path(task.output_path).stat().st_size
            task.progress = DownloadProgress(
                downloaded=actual_size,
                total=task.os_info.size or actual_size,
                speed=0,
                eta=0
            )

            logger.info(f"Download completed: {Path(task.output_path).name}")
            if task.on_complete:
                task.on_complete(True, None)

        except Exception as e:
            task.state = DownloadState.FAILED
            task.error_message = f"Verification failed: {e}"
            logger.error(task.error_message)
            if task.on_complete:
                task.on_complete(False, task.error_message)

    @staticmethod
    def _verify_checksum_python(file_path: str, expected: str, algorithm: str) -> bool:
        """Verify file checksum using pure Python."""
        path = Path(file_path)

        algorithm_lower = algorithm.lower()

        if algorithm_lower == "sha256":
            hasher = hashlib.sha256()
        elif algorithm_lower == "md5":
            hasher = hashlib.md5()
        elif algorithm_lower == "sha1":
            hasher = hashlib.sha1()
        elif algorithm_lower == "sha512":
            hasher = hashlib.sha512()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

        with open(path, "rb") as f:
            while chunk := f.read(65536):  # Read in larger chunks
                hasher.update(chunk)

        calculated = hasher.hexdigest()
        return calculated.lower() == expected.lower()

    @staticmethod
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

    def get_task_info(self, url: str) -> dict:
        """
        Get information about a download URL without downloading.

        Args:
            url: The URL to check

        Returns:
            Dictionary with file info
        """
        if HAS_RUST:
            from core import _core
            info = _core.get_file_info(url)
            return {
                "size": info.size,
                "supports_resume": info.supports_range,
                "content_type": info.content_type,
            }
        else:
            # Pure Python fallback with SSL handling
            try:
                response = _download_session.head(url, timeout=15, verify=True)
                return {
                    "size": int(response.headers.get("content-length", 0)),
                    "supports_resume": response.headers.get("accept-ranges", "").lower() == "bytes",
                    "content_type": response.headers.get("content-type", "application/octet-stream"),
                }
            except requests.exceptions.SSLError:
                # Fall back to no SSL verification
                response = _download_session.head(url, timeout=15, verify=False)
                return {
                    "size": int(response.headers.get("content-length", 0)),
                    "supports_resume": response.headers.get("accept-ranges", "").lower() == "bytes",
                    "content_type": response.headers.get("content-type", "application/octet-stream"),
                }
            except Exception as e:
                logger.error(f"Failed to get file info: {e}")
                return {
                    "size": 0,
                    "supports_resume": False,
                    "content_type": "application/octet-stream",
                }

    def pause_download(self, task: DownloadTask) -> bool:
        """
        Pause a download task.

        Note: This is a soft pause - the current chunk will finish.
        """
        if task.state == DownloadState.DOWNLOADING:
            task.state = DownloadState.PAUSED
            return True
        return False

    def resume_download(self, task: DownloadTask) -> bool:
        """Resume a paused download."""
        if task.state == DownloadState.PAUSED:
            return self.start_download(task)
        return False

    def cancel_download(self, task: DownloadTask) -> bool:
        """Cancel a download task."""
        if task.state in (DownloadState.DOWNLOADING, DownloadState.PAUSED, DownloadState.PENDING):
            task.cancel()
            return True
        return False

    def clear_completed(self) -> int:
        """
        Remove all completed tasks from the active list.

        Returns:
            Number of tasks cleared
        """
        count = 0
        for task in self._active_tasks[:]:
            if task.state in (DownloadState.COMPLETED, DownloadState.FAILED, DownloadState.CANCELLED):
                self._active_tasks.remove(task)
                count += 1
        return count
