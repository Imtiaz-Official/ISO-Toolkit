"""
Download manager for handling ISO downloads with resume support.
"""

import os
import time
import threading
import hashlib
from pathlib import Path
from typing import Optional, List
from datetime import datetime
import requests

from iso_toolkit.models import (
    DownloadTask,
    DownloadState,
    DownloadProgress,
    OSInfo,
)


def _has_rust_extension() -> bool:
    """Check if Rust extension is available."""
    try:
        from iso_toolkit import _core
        return True
    except ImportError:
        return False


HAS_RUST = _has_rust_extension()


class DownloadManager:
    """
    Manages ISO downloads with resume support, progress tracking, and checksum verification.
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
                print(f"Resuming download from {self._format_bytes(file_size)}")
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
        """Worker thread that handles the actual download."""
        try:
            if HAS_RUST:
                self._download_with_rust(task, resume)
            else:
                self._download_with_python(task, resume)

        except Exception as e:
            task.state = DownloadState.FAILED
            task.error_message = str(e)
            if task.on_complete:
                task.on_complete(False, str(e))

        finally:
            if task.state in (DownloadState.COMPLETED, DownloadState.FAILED, DownloadState.CANCELLED):
                if task not in self._completed_tasks:
                    self._completed_tasks.append(task)

    def _download_with_rust(self, task: DownloadTask, resume: bool) -> None:
        """Download using Rust extension (faster)."""
        from iso_toolkit import _core

        def progress_callback(downloaded: int, total: int) -> bool:
            if task.is_cancelled():
                return False

            self._update_task_progress(task, downloaded, total)
            return True

        result = _core.download_file(
            task.os_info.url,
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
            if task.on_complete:
                task.on_complete(False, task.error_message)

    def _download_with_python(self, task: DownloadTask, resume: bool) -> None:
        """Download using pure Python (fallback)."""
        path = Path(task.output_path)
        start_pos = 0

        # Check for resume
        if resume and path.exists():
            start_pos = path.stat().st_size

        headers = {}
        if start_pos > 0:
            headers["Range"] = f"bytes={start_pos}-"

        response = requests.get(task.os_info.url, headers=headers, stream=True, timeout=30)

        if response.status_code not in (200, 206):
            task.state = DownloadState.FAILED
            task.error_message = f"HTTP error: {response.status_code}"
            if task.on_complete:
                task.on_complete(False, task.error_message)
            return

        # Get total size
        total_size = start_pos
        if "content-length" in response.headers:
            total_size += int(response.headers["content-length"])
        elif task.os_info.size:
            total_size = task.os_info.size

        mode = "ab" if resume and start_pos > 0 else "wb"

        with open(path, mode) as f:
            downloaded = start_pos
            chunk_size = 8192

            for chunk in response.iter_content(chunk_size=chunk_size):
                if task.is_cancelled():
                    task.state = DownloadState.CANCELLED
                    return

                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    self._update_task_progress(task, downloaded, total_size)

        if not task.is_cancelled():
            task.state = DownloadState.VERIFYING
            self._verify_and_complete(task)

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
            except Exception:
                pass

    def _verify_and_complete(self, task: DownloadTask) -> None:
        """Verify checksum and mark task as complete."""
        try:
            if task.os_info.checksum and task.os_info.checksum_type:
                task.state = DownloadState.VERIFYING

                if HAS_RUST:
                    from iso_toolkit import _core
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
                    if task.on_complete:
                        task.on_complete(False, task.error_message)
                    return

            task.state = DownloadState.COMPLETED
            task.completed_at = datetime.now()
            task.progress = DownloadProgress(
                downloaded=task.os_info.size or Path(task.output_path).stat().st_size,
                total=task.os_info.size or Path(task.output_path).stat().st_size,
                speed=0,
                eta=0
            )

            if task.on_complete:
                task.on_complete(True, None)

        except Exception as e:
            task.state = DownloadState.FAILED
            task.error_message = f"Verification failed: {e}"
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
            while chunk := f.read(8192):
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
            from iso_toolkit import _core
            info = _core.get_file_info(url)
            return {
                "size": info.size,
                "supports_resume": info.supports_range,
                "content_type": info.content_type,
            }
        else:
            # Pure Python fallback
            try:
                response = requests.head(url, timeout=10)
                return {
                    "size": int(response.headers.get("content-length", 0)),
                    "supports_resume": response.headers.get("accept-ranges", "").lower() == "bytes",
                    "content_type": response.headers.get("content-type", "application/octet-stream"),
                }
            except Exception:
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
