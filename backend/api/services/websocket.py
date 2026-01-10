"""
WebSocket connection manager for real-time download progress updates.
"""

from fastapi import WebSocket
from typing import Dict, Set
import json
import logging

logger = logging.getLogger(__name__)


class DownloadWebSocketManager:
    """
    Manages WebSocket connections for real-time download progress updates.

    Each client can subscribe to specific downloads or all downloads.
    """

    def __init__(self):
        # Active WebSocket connections by client ID
        self.active_connections: Dict[str, WebSocket] = {}
        # Subscriptions: which downloads each client is watching
        self.subscriptions: Dict[str, Set[int]] = {}
        # Counter for generating client IDs
        self._client_counter = 0

    async def connect(self, websocket: WebSocket) -> str:
        """
        Accept a new WebSocket connection.

        Args:
            websocket: The WebSocket connection

        Returns:
            Client ID for this connection
        """
        await websocket.accept()
        self._client_counter += 1
        client_id = f"client_{self._client_counter}"
        self.active_connections[client_id] = websocket
        self.subscriptions[client_id] = set()
        logger.info(f"WebSocket client connected: {client_id}")
        return client_id

    def disconnect(self, client_id: str) -> None:
        """
        Disconnect a WebSocket client.

        Args:
            client_id: The client ID to disconnect
        """
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.subscriptions:
            del self.subscriptions[client_id]
        logger.info(f"WebSocket client disconnected: {client_id}")

    async def send_personal_message(self, message: dict, client_id: str) -> bool:
        """
        Send a message to a specific client.

        Args:
            message: The message to send (will be JSON encoded)
            client_id: The client ID to send to

        Returns:
            True if message was sent successfully, False otherwise
        """
        if client_id not in self.active_connections:
            return False

        try:
            websocket = self.active_connections[client_id]
            await websocket.send_json(message)
            return True
        except Exception as e:
            logger.error(f"Error sending message to {client_id}: {e}")
            # Remove dead connection
            self.disconnect(client_id)
            return False

    async def broadcast(self, message: dict) -> None:
        """
        Broadcast a message to all connected clients.

        Args:
            message: The message to broadcast (will be JSON encoded)
        """
        # Use list() to avoid dictionary size change during iteration
        for client_id in list(self.active_connections.keys()):
            await self.send_personal_message(message, client_id)

    async def broadcast_download_progress(self, download_id: int, progress: dict) -> None:
        """
        Broadcast download progress to clients subscribed to this download.

        Args:
            download_id: The download ID
            progress: The progress data
        """
        message = {
            "type": "download_progress",
            "download_id": download_id,
            "data": progress
        }

        # Send to all clients subscribed to this download
        for client_id, subscribed_downloads in self.subscriptions.items():
            if download_id in subscribed_downloads or len(subscribed_downloads) == 0:
                await self.send_personal_message(message, client_id)

    def subscribe_to_download(self, client_id: str, download_id: int) -> None:
        """
        Subscribe a client to updates for a specific download.

        Args:
            client_id: The client ID
            download_id: The download ID to subscribe to
        """
        if client_id in self.subscriptions:
            self.subscriptions[client_id].add(download_id)
            logger.info(f"Client {client_id} subscribed to download {download_id}")

    def unsubscribe_from_download(self, client_id: str, download_id: int) -> None:
        """
        Unsubscribe a client from updates for a specific download.

        Args:
            client_id: The client ID
            download_id: The download ID to unsubscribe from
        """
        if client_id in self.subscriptions:
            self.subscriptions[client_id].discard(download_id)
            logger.info(f"Client {client_id} unsubscribed from download {download_id}")

    def subscribe_to_all(self, client_id: str) -> None:
        """
        Subscribe a client to all download updates.

        Args:
            client_id: The client ID
        """
        if client_id in self.subscriptions:
            self.subscriptions[client_id] = set()  # Empty set = subscribe to all
            logger.info(f"Client {client_id} subscribed to all downloads")

    def get_connection_count(self) -> int:
        """Get the number of active WebSocket connections."""
        return len(self.active_connections)


# Global WebSocket manager instance
ws_manager = DownloadWebSocketManager()
