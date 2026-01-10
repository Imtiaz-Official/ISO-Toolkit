"""
Download service for managing ISO downloads with WebSocket progress updates.

Integrates with the existing DownloadManager but adds async support
and WebSocket progress broadcasting.
"""

import asyncio
import os
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
import logging

from sqlalchemy.orm import Session

from core.models import (
    DownloadTask,
    DownloadState,
    DownloadProgress,
    OSInfo,
)
from core.manager import DownloadManager
from api.database.models import DownloadRecord
from api.services.websocket import ws_manager

logger = logging.getLogger(__name__)


class AsyncDownloadService:
    """
    Async download service that manages downloads with WebSocket updates.
    """

    def __init__(self, download_dir: Optional[str] = None):
        """
        Initialize the download service.

        Args:
            download_dir: Directory for downloads (default: ~/Downloads/ISOs)
        """
        self.download_manager = DownloadManager(download_dir)
        self.active_tasks: Dict[int, DownloadTask] = {}
        self._task_counter = 0

    async def start_download(
        self,
        os_info: OSInfo,
        db: Session,
        output_path: Optional[str] = None,
    ) -> DownloadRecord:
        """
        Start a new download.

        Args:
            os_info: Information about the OS to download
            db: Database session
            output_path: Custom output path (optional)

        Returns:
            DownloadRecord database record
        """
        # Generate output path if not provided
        if output_path is None:
            output_path = self.download_manager.get_output_path(os_info)

        # Create database record
        record = DownloadRecord(
            os_name=os_info.name,
            os_version=os_info.version,
            os_category=os_info.category.value,
            os_architecture=os_info.architecture.value,
            os_language=os_info.language,
            url=os_info.url,
            output_path=output_path,
            state=DownloadState.PENDING,
            checksum=os_info.checksum,
            checksum_type=os_info.checksum_type,
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        # Create download task
        task = DownloadTask(
            os_info=os_info,
            output_path=output_path,
            state=DownloadState.PENDING,
        )

        # Set up progress callback for WebSocket
        def on_progress(progress: DownloadProgress):
            asyncio.create_task(self._broadcast_progress(record.id, progress))

        # Set up completion callback (async version stored separately)
        async def on_complete_async(success: bool, error: Optional[str] = None):
            await self._on_download_complete(record.id, db, success, error)

        # Synchronous wrapper for the manager's _download_worker
        def on_complete(success: bool, error: Optional[str] = None):
            # Schedule the async callback to run in the event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(on_complete_async(success, error))

        # Store task and callbacks
        self.active_tasks[record.id] = task
        task.on_progress = on_progress
        task.on_complete = on_complete
        task._on_complete_async = on_complete_async

        # Start download in background
        asyncio.create_task(self._run_download(record.id))

        return record

    async def _run_download(self, download_id: int) -> None:
        """
        Run the download in background.

        Args:
            download_id: The download ID
        """
        if download_id not in self.active_tasks:
            return

        task = self.active_tasks[download_id]

        # Update state to downloading
        task.state = DownloadState.DOWNLOADING
        task.started_at = datetime.now()

        await self._update_db_state(download_id, DownloadState.DOWNLOADING)

        # Start the actual download (run in thread pool since it's blocking)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.download_manager.start_download, task)

    async def _broadcast_progress(self, download_id: int, progress: DownloadProgress) -> None:
        """
        Broadcast download progress via WebSocket.

        Args:
            download_id: The download ID
            progress: The progress data
        """
        progress_data = {
            "state": progress.state.value,
            "progress": progress.percentage,
            "downloaded_bytes": progress.downloaded,
            "total_bytes": progress.total,
            "downloaded_formatted": progress.downloaded_formatted,
            "total_formatted": progress.total_formatted,
            "speed": progress.speed,
            "speed_formatted": progress.speed_formatted,
            "eta": progress.eta,
            "eta_formatted": progress.eta_formatted,
        }

        await ws_manager.broadcast_download_progress(download_id, progress_data)

        # Also update database periodically (every 10% or on state change)
        if int(progress.percentage) % 10 == 0 or progress.state in (
            DownloadState.COMPLETED,
            DownloadState.FAILED,
        ):
            await self._update_db_progress(download_id, progress)

    async def _on_download_complete(
        self,
        download_id: int,
        db: Session,
        success: bool,
        error: Optional[str] = None,
    ) -> None:
        """
        Handle download completion.

        Args:
            download_id: The download ID
            db: Database session
            success: Whether download succeeded
            error: Error message if failed
        """
        record = db.query(DownloadRecord).filter(DownloadRecord.id == download_id).first()
        if not record:
            return

        if success:
            record.state = DownloadState.COMPLETED
            record.completed_at = datetime.utcnow()
            record.progress = 100.0
            record.checksum_verified = 1
        else:
            record.state = DownloadState.FAILED
            record.error_message = error
            record.checksum_verified = -1

        db.commit()

        # Broadcast final update
        await ws_manager.broadcast_download_progress(
            download_id,
            {
                "state": record.state.value,
                "progress": record.progress,
                "error_message": record.error_message,
                "checksum_verified": record.checksum_verified,
            },
        )

        # Remove from active tasks
        if download_id in self.active_tasks:
            del self.active_tasks[download_id]

    async def _update_db_state(self, download_id: int, state: DownloadState) -> None:
        """
        Update download state in database.

        Args:
            download_id: The download ID
            state: The new state
        """
        from api.database.session import SessionLocal

        db = SessionLocal()
        try:
            record = db.query(DownloadRecord).filter(DownloadRecord.id == download_id).first()
            if record:
                record.state = state
                if state == DownloadState.DOWNLOADING and not record.started_at:
                    record.started_at = datetime.utcnow()
                db.commit()
        finally:
            db.close()

    async def _update_db_progress(self, download_id: int, progress: DownloadProgress) -> None:
        """
        Update download progress in database.

        Args:
            download_id: The download ID
            progress: The progress data
        """
        from api.database.session import SessionLocal

        db = SessionLocal()
        try:
            record = db.query(DownloadRecord).filter(DownloadRecord.id == download_id).first()
            if record:
                record.state = progress.state
                record.progress = progress.percentage
                record.downloaded_bytes = progress.downloaded
                record.total_bytes = progress.total
                record.speed = progress.speed
                record.eta = progress.eta
                db.commit()
        finally:
            db.close()

    async def pause_download(self, download_id: int) -> bool:
        """
        Pause a download.

        Args:
            download_id: The download ID

        Returns:
            True if paused successfully
        """
        if download_id not in self.active_tasks:
            return False

        task = self.active_tasks[download_id]
        result = self.download_manager.pause_download(task)

        if result:
            await self._update_db_state(download_id, DownloadState.PAUSED)
            await ws_manager.broadcast_download_progress(
                download_id,
                {"state": DownloadState.PAUSED.value},
            )

        return result

    async def resume_download(self, download_id: int) -> bool:
        """
        Resume a paused download.

        Args:
            download_id: The download ID

        Returns:
            True if resumed successfully
        """
        if download_id not in self.active_tasks:
            return False

        task = self.active_tasks[download_id]
        result = self.download_manager.resume_download(task)

        if result:
            asyncio.create_task(self._run_download(download_id))

        return result

    async def cancel_download(self, download_id: int) -> bool:
        """
        Cancel a download.

        Args:
            download_id: The download ID

        Returns:
            True if cancelled successfully (always returns True to allow UI to proceed)
        """
        from api.database.session import SessionLocal

        logger.info(f"Cancel request for download {download_id}, active_tasks: {list(self.active_tasks.keys())}")

        # If download is active, cancel it normally
        if download_id in self.active_tasks:
            task = self.active_tasks[download_id]
            logger.info(f"Download {download_id} found in active_tasks, state: {task.state}")
            result = self.download_manager.cancel_download(task)
            logger.info(f"DownloadManager.cancel_download returned: {result}")

            if result:
                await self._update_db_state(download_id, DownloadState.CANCELLED)
                await ws_manager.broadcast_download_progress(
                    download_id,
                    {"state": DownloadState.CANCELLED.value},
                )
                if download_id in self.active_tasks:
                    del self.active_tasks[download_id]
                return True

        # If download is not active or cancel failed, try to mark it as cancelled in database
        # This handles all edge cases: server restart, race conditions, stuck downloads
        db = SessionLocal()
        try:
            record = db.query(DownloadRecord).filter(DownloadRecord.id == download_id).first()
            if record:
                logger.info(f"Download {download_id} found in DB, state: {record.state}")
                # Always mark as cancelled regardless of current state
                # This allows users to dismiss stuck or completed downloads
                old_state = record.state
                record.state = DownloadState.CANCELLED
                db.commit()
                logger.info(f"Download {download_id} marked as cancelled (was: {old_state})")
                await ws_manager.broadcast_download_progress(
                    download_id,
                    {"state": DownloadState.CANCELLED.value},
                )
                return True
            else:
                logger.warning(f"Download {download_id} not found in database")
                return False
        finally:
            db.close()

    def get_all_downloads(self, db: Session) -> List[DownloadRecord]:
        """
        Get all downloads from database.

        Args:
            db: Database session

        Returns:
            List of all download records
        """
        return db.query(DownloadRecord).order_by(DownloadRecord.created_at.desc()).all()

    def get_download(self, download_id: int, db: Session) -> Optional[DownloadRecord]:
        """
        Get a specific download from database.

        Args:
            download_id: The download ID
            db: Database session

        Returns:
            Download record or None
        """
        return db.query(DownloadRecord).filter(DownloadRecord.id == download_id).first()

    async def clear_completed(self, db: Session) -> int:
        """
        Clear completed downloads from database.

        Args:
            db: Database session

        Returns:
            Number of downloads cleared
        """
        completed = (
            db.query(DownloadRecord)
            .filter(DownloadRecord.state.in_(
                [DownloadState.COMPLETED, DownloadState.FAILED, DownloadState.CANCELLED]
            ))
            .all()
        )

        count = len(completed)
        for record in completed:
            db.delete(record)

        db.commit()
        return count


# Global download service instance
download_service = AsyncDownloadService()
