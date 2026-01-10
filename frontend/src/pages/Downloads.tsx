/**
 * Downloads page - View and manage downloads with real-time progress.
 * Mobile responsive design with animations.
 */

import { useEffect, useState, useCallback, useRef } from 'react';
import { downloadsAPI } from '../services/api';
import { useWebSocket } from '../hooks/useWebSocket';
import type { DownloadStatus, DownloadState, DownloadProgressUpdate } from '../types';

export default function DownloadsPage() {
  const [downloads, setDownloads] = useState<DownloadStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const progressMapRef = useRef(new Map<number, DownloadStatus>());

  const { connected } = useWebSocket((update: DownloadProgressUpdate) => {
    // Update download with new progress
    setDownloads((prev) =>
      prev.map((dl) =>
        dl.id === update.download_id
          ? {
              ...dl,
              state: update.data.state,
              progress: update.data.progress,
              downloaded_bytes: update.data.downloaded_bytes,
              total_bytes: update.data.total_bytes,
              downloaded_formatted: update.data.downloaded_formatted,
              total_formatted: update.data.total_formatted,
              speed: update.data.speed,
              speed_formatted: update.data.speed_formatted,
              eta: update.data.eta,
              eta_formatted: update.data.eta_formatted,
              error_message: update.data.error_message ?? null,
              checksum_verified: update.data.checksum_verified ?? null,
            }
          : dl
      )
    );
  });

  const loadDownloads = useCallback(async () => {
    try {
      const data = await downloadsAPI.getAll();
      setDownloads(data);
      // Store for reference
      data.forEach((dl) => progressMapRef.current.set(dl.id, dl));
    } catch (error) {
      console.error('Failed to load downloads:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDownloads();
    // Refresh every 2 seconds
    const interval = setInterval(loadDownloads, 2000);
    return () => clearInterval(interval);
  }, [loadDownloads]);

  async function handlePause(downloadId: number) {
    try {
      await downloadsAPI.pause(downloadId);
      await loadDownloads();
    } catch (error) {
      console.error('Failed to pause download:', error);
    }
  }

  async function handleResume(downloadId: number) {
    try {
      await downloadsAPI.resume(downloadId);
      await loadDownloads();
    } catch (error) {
      console.error('Failed to resume download:', error);
    }
  }

  async function handleCancel(downloadId: number) {
    if (!confirm('Are you sure you want to cancel this download?')) {
      return;
    }
    try {
      await downloadsAPI.cancel(downloadId);
      await loadDownloads();
    } catch (error) {
      console.error('Failed to cancel download:', error);
    }
  }

  async function handleClearCompleted() {
    if (!confirm('Clear all completed, failed, and cancelled downloads?')) {
      return;
    }
    try {
      await downloadsAPI.clearCompleted();
      await loadDownloads();
    } catch (error) {
      console.error('Failed to clear completed:', error);
    }
  }

  async function handleDismiss(downloadId: number) {
    try {
      await downloadsAPI.delete(downloadId);
      // Remove from local state immediately for instant feedback
      setDownloads(prev => prev.filter(d => d.id !== downloadId));
    } catch (error) {
      console.error('Failed to dismiss download:', error);
      // Refresh to get actual state
      await loadDownloads();
    }
  }

  function getStateColor(state: DownloadState): string {
    switch (state) {
      case 'downloading':
        return 'text-blue-600 bg-blue-50 dark:bg-blue-900/20';
      case 'paused':
        return 'text-yellow-600 bg-yellow-50 dark:bg-yellow-900/20';
      case 'completed':
        return 'text-green-600 bg-green-50 dark:bg-green-900/20';
      case 'failed':
        return 'text-red-600 bg-red-50 dark:bg-red-900/20';
      case 'cancelled':
        return 'text-gray-600 bg-gray-50 dark:bg-gray-900/20';
      default:
        return 'text-gray-600 bg-gray-50 dark:bg-gray-900/20';
    }
  }

  function getStateIcon(state: DownloadState): string {
    switch (state) {
      case 'downloading':
        return '⬇️';
      case 'paused':
        return '⏸️';
      case 'completed':
        return '✅';
      case 'failed':
        return '❌';
      case 'cancelled':
        return '🚫';
      default:
        return '⏳';
    }
  }

  const completedCount = downloads.filter((d) =>
    d.state === 'completed' || d.state === 'failed' || d.state === 'cancelled'
  ).length;

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-3">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">Downloads</h1>
          <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400 mt-1">
            {connected ? (
              <span className="text-green-600">Connected - Real-time updates</span>
            ) : (
              <span className="text-yellow-600">Connecting...</span>
            )}
          </p>
        </div>
        {completedCount > 0 && (
          <button onClick={handleClearCompleted} className="btn btn-secondary text-sm sm:text-base w-full sm:w-auto">
            Clear Completed ({completedCount})
          </button>
        )}
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center h-48 sm:h-64">
          <div className="flex flex-col items-center space-y-3 sm:space-y-4">
            <div className="animate-spin rounded-full h-10 w-10 sm:h-12 sm:w-12 border-b-2 border-blue-600"></div>
            <p className="text-sm text-gray-500 dark:text-gray-400">Loading downloads...</p>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!loading && downloads.length === 0 && (
        <div className="text-center py-8 sm:py-12 px-4">
          <div className="text-5xl sm:text-6xl mb-4">📥</div>
          <h3 className="text-lg sm:text-xl font-semibold text-gray-900 dark:text-white mb-2">No Downloads Yet</h3>
          <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400 mb-4 sm:mb-6">Start by browsing and downloading an OS</p>
          <a href="/browse" className="btn btn-primary text-sm sm:text-base">
            Browse ISOs
          </a>
        </div>
      )}

      {/* Downloads List */}
      {!loading && downloads.length > 0 && (
        <div className="space-y-3 sm:space-y-4">
          {downloads.map((download) => (
            <DownloadCard
              key={download.id}
              download={download}
              onPause={handlePause}
              onResume={handleResume}
              onCancel={handleCancel}
              onDismiss={handleDismiss}
              getStateColor={getStateColor}
              getStateIcon={getStateIcon}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function DownloadCard({
  download,
  onPause,
  onResume,
  onCancel,
  onDismiss,
  getStateColor,
  getStateIcon,
}: {
  download: DownloadStatus;
  onPause: (id: number) => void;
  onResume: (id: number) => void;
  onCancel: (id: number) => void;
  onDismiss: (id: number) => void;
  getStateColor: (state: DownloadState) => string;
  getStateIcon: (state: DownloadState) => string;
}) {
  const isDownloading = download.state === 'downloading';
  const isPaused = download.state === 'paused';
  const isCompleted = download.state === 'completed';
  const isFailed = download.state === 'failed';
  const isCancelled = download.state === 'cancelled';

  return (
    <div className="card p-3 sm:p-4 transition-all duration-300 hover:shadow-lg">
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2 sm:gap-0 mb-3 sm:mb-4">
        <div className="flex items-center space-x-2 sm:space-x-3">
          <span className="text-xl sm:text-2xl">{download.os_icon || '💿'}</span>
          <div className="min-w-0 flex-1">
            <h3 className="font-semibold text-sm sm:text-lg text-gray-900 dark:text-white truncate">{download.os_name}</h3>
            <p className="text-xs sm:text-sm text-gray-500 dark:text-gray-400">{download.os_version} - {download.os_architecture}</p>
          </div>
        </div>
        <span className={`px-2 sm:px-3 py-1 rounded-full text-xs sm:text-sm font-medium ${getStateColor(download.state)} self-start`}>
          {getStateIcon(download.state)} {download.state.charAt(0).toUpperCase() + download.state.slice(1)}
        </span>
      </div>

      {/* Progress Bar - Animated */}
      {(isDownloading || isPaused) && download.total_bytes > 0 && (
        <div className="mb-3 sm:mb-4">
          <div className="flex justify-between text-xs sm:text-sm mb-1">
            <span className="text-gray-600 dark:text-gray-400">
              {download.downloaded_formatted} / {download.total_formatted}
            </span>
            <span className="font-medium text-gray-900 dark:text-white">{download.progress.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
            <div
              className="bg-gradient-to-r from-blue-500 to-blue-600 h-2 rounded-full transition-all duration-300 ease-out"
              style={{ width: `${download.progress}%` }}
            />
          </div>
          <div className="flex justify-between text-xs sm:text-sm text-gray-500 dark:text-gray-400 mt-1">
            <span className="font-medium">{download.speed_formatted}</span>
            <span>ETA: {download.eta_formatted}</span>
          </div>
        </div>
      )}

      {/* Completed/Failed State */}
      {isCompleted && (
        <div className="mb-3 sm:mb-4 p-2 sm:p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg animate-fade-in">
          <div className="flex items-center text-green-700 dark:text-green-400 text-xs sm:text-sm">
            <svg className="w-4 h-4 sm:w-5 sm:h-5 mr-2 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <span className="break-all font-medium">Download Complete!</span>
          </div>
          <div className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mt-1 truncate flex items-center">
            <svg className="w-4 h-4 sm:w-4 sm:h-4 mr-2 flex-shrink-0 text-gray-500" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
            </svg>
            <span className="truncate">{download.output_path}</span>
          </div>
          {download.checksum_verified === 1 && (
            <div className="text-xs sm:text-sm text-green-600 dark:text-green-500 mt-1 flex items-center">
              <svg className="w-4 h-4 sm:w-4 sm:h-4 mr-1 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span>Checksum verified</span>
            </div>
          )}
        </div>
      )}

      {isFailed && (
        <div className="mb-3 sm:mb-4 p-2 sm:p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg animate-fade-in">
          <div className="flex items-center text-red-700 dark:text-red-400 text-xs sm:text-sm">
            <svg className="w-4 h-4 sm:w-5 sm:h-5 mr-2 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <span className="font-medium">Download Failed</span>
          </div>
          {download.error_message && (
            <div className="text-xs sm:text-sm text-red-600 dark:text-red-500 mt-1 break-all">{download.error_message}</div>
          )}
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-2">
        {isDownloading && (
          <>
            <button
              onClick={() => onPause(download.id)}
              className="btn btn-secondary text-xs sm:text-sm flex-1 sm:flex-initial transition-transform hover:scale-105"
            >
              <svg className="w-4 h-4" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              Pause
            </button>
            <button
              onClick={() => onCancel(download.id)}
              className="btn btn-danger text-xs sm:text-sm flex-1 sm:flex-initial transition-transform hover:scale-105"
            >
              <svg className="w-4 h-4" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              Cancel
            </button>
          </>
        )}
        {isPaused && (
          <>
            <button
              onClick={() => onResume(download.id)}
              className="btn btn-primary text-xs sm:text-sm flex-1 sm:flex-initial transition-transform hover:scale-105"
            >
              <svg className="w-4 h-4" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
              </svg>
              Resume
            </button>
            <button
              onClick={() => onCancel(download.id)}
              className="btn btn-danger text-xs sm:text-sm flex-1 sm:flex-initial transition-transform hover:scale-105"
            >
              <svg className="w-4 h-4" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              Cancel
            </button>
          </>
        )}
        {(isCompleted || isFailed || isCancelled) && (
          <button
            onClick={() => onDismiss(download.id)}
            className="btn btn-secondary text-xs sm:text-sm transition-transform hover:scale-105"
          >
            <svg className="w-4 h-4" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            Dismiss
          </button>
        )}
      </div>
    </div>
  );
}
