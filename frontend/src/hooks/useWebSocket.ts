/**
 * Custom hook for managing WebSocket connection to download progress updates.
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import type { WebSocketMessage, DownloadProgressUpdate } from '../types';

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://127.0.0.1:8000/api/ws/downloads';

interface UseWebSocketReturn {
  connected: boolean;
  clientId: string | null;
  progressUpdates: Map<number, DownloadProgressUpdate['data']>;
  subscribeToDownload: (downloadId: number) => void;
  unsubscribeFromDownload: (downloadId: number) => void;
  send: (data: any) => void;
  connect: () => void;
  disconnect: () => void;
}

export function useWebSocket(onProgress?: (update: DownloadProgressUpdate) => void): UseWebSocketReturn {
  const [connected, setConnected] = useState(false);
  const [clientId, setClientId] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const progressUpdatesRef = useRef(new Map<number, DownloadProgressUpdate['data']>());
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const onProgressRef = useRef(onProgress);

  // Keep callback updated
  useEffect(() => {
    onProgressRef.current = onProgress;
  }, [onProgress]);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);

          if (message.type === 'connected') {
            setClientId(message.client_id || null);
          } else if (message.type === 'download_progress' && message.download_id !== undefined) {
            const update: DownloadProgressUpdate = {
              type: 'download_progress',
              download_id: message.download_id,
              data: message.data,
            };

            // Store progress update
            progressUpdatesRef.current.set(message.download_id, message.data);

            // Call callback
            if (onProgressRef.current) {
              onProgressRef.current(update);
            }
          }
        } catch (e) {
          console.error('Error parsing WebSocket message:', e);
        }
      };

      ws.onclose = () => {
        setConnected(false);
        setClientId(null);

        // Attempt to reconnect after 3 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, 3000);
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
    }
  }, []);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setConnected(false);
    setClientId(null);
  }, []);

  const subscribeToDownload = useCallback((downloadId: number) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'subscribe',
        download_id: downloadId,
      }));
    }
  }, []);

  const unsubscribeFromDownload = useCallback((downloadId: number) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'unsubscribe',
        download_id: downloadId,
      }));
    }
  }, []);

  const send = useCallback((data: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  }, []);

  // Auto-connect on mount
  useEffect(() => {
    connect();
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    connected,
    clientId,
    progressUpdates: progressUpdatesRef.current,
    subscribeToDownload,
    unsubscribeFromDownload,
    send,
    connect,
    disconnect,
  };
}
