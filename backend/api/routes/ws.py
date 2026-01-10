"""
WebSocket routes for real-time download progress updates.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional

from api.services.websocket import ws_manager

router = APIRouter(prefix="/api/ws", tags=["WebSocket"])


@router.websocket("/downloads")
async def downloads_websocket(
    websocket: WebSocket,
    subscribe_all: bool = Query(False, description="Subscribe to all downloads"),
    subscribe_download: Optional[int] = Query(None, description="Subscribe to specific download"),
):
    """
    WebSocket endpoint for real-time download progress updates.

    Clients can subscribe to:
    - All downloads (subscribe_all=true)
    - Specific download (subscribe_download=ID)

    Message format:
    {
        "type": "download_progress",
        "download_id": int,
        "data": {
            "state": str,
            "progress": float,
            "downloaded_bytes": int,
            "total_bytes": int,
            "speed": float,
            "eta": int,
            ...
        }
    }
    """
    # Accept connection
    client_id = await ws_manager.connect(websocket)

    try:
        # Handle subscriptions
        if subscribe_all:
            ws_manager.subscribe_to_all(client_id)
        elif subscribe_download is not None:
            ws_manager.subscribe_to_download(client_id, subscribe_download)
        else:
            # By default, subscribe to all
            ws_manager.subscribe_to_all(client_id)

        # Send initial connection message
        await websocket.send_json({
            "type": "connected",
            "client_id": client_id,
            "message": "WebSocket connection established",
        })

        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_json()

            # Handle client messages
            if data.get("type") == "subscribe":
                download_id = data.get("download_id")
                if download_id is not None:
                    ws_manager.subscribe_to_download(client_id, download_id)
            elif data.get("type") == "unsubscribe":
                download_id = data.get("download_id")
                if download_id is not None:
                    ws_manager.unsubscribe_from_download(client_id, download_id)
            elif data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        ws_manager.disconnect(client_id)
    except Exception as e:
        ws_manager.disconnect(client_id)
        raise
