/**
 * TypeScript type definitions for ISO Toolkit web application.
 */

export type OSCategory = 'windows' | 'linux' | 'macos' | 'bsd' | 'other';

export type Architecture = 'x64' | 'x86' | 'arm64' | 'arm' | 'riscv64' | 'universal';

export type DownloadState = 'pending' | 'downloading' | 'paused' | 'completed' | 'failed' | 'verifying' | 'cancelled';

export interface OSInfo {
  id: string;
  name: string;
  version: string;
  category: OSCategory;
  architecture: Architecture;
  language: string;
  size: number | null;
  size_formatted: string;
  source: string | null;
  icon: string;
  url: string;
  checksum: string | null;
  checksum_type: string | null;
  description: string | null;
  release_date: string | null;
  subcategory: string | null;
}

export interface DownloadStatus {
  id: number;
  os_name: string;
  os_version: string;
  os_category: string;
  os_architecture: string;
  os_icon: string | null;
  state: DownloadState;
  progress: number;
  downloaded_bytes: number;
  total_bytes: number;
  downloaded_formatted: string;
  total_formatted: string;
  speed: number;
  speed_formatted: string;
  eta: number;
  eta_formatted: string;
  created_at: string | null;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
  checksum_verified: number | null;
  output_path: string;
}

export interface DownloadProgressUpdate {
  type: 'download_progress';
  download_id: number;
  data: {
    state: DownloadState;
    progress: number;
    downloaded_bytes: number;
    total_bytes: number;
    downloaded_formatted: string;
    total_formatted: string;
    speed: number;
    speed_formatted: string;
    eta: number;
    eta_formatted: string;
    error_message?: string;
    checksum_verified?: number;
  };
}

export interface WebSocketMessage {
  type: 'connected' | 'download_progress' | 'pong';
  client_id?: string;
  message?: string;
  download_id?: number;
  data?: any;
}

export interface OSCategory {
  category: OSCategory;
  name: string;
  icon: string;
  count: number;
}

export interface LinuxSubcategory {
  subcategory: string;
  name: string;
  icon: string;
  count: number;
}

export interface Stats {
  total_downloads: number;
  active_downloads: number;
  completed_downloads: number;
  failed_downloads: number;
  total_bytes_downloaded: number;
  total_bytes_formatted: string;
}

export interface Settings {
  download_directory: string;
  max_concurrent_downloads: number;
  auto_start_downloads: boolean;
  theme: 'light' | 'dark' | 'auto';
}
