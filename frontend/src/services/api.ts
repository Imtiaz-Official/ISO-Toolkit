/**
 * API service for communicating with the FastAPI backend.
 */

import axios from 'axios';
import type { OSInfo, DownloadStatus, OSCategory, OSCategoryResponse, Stats, LinuxSubcategory } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * OS API
 */
export const osAPI = {
  /**
   * Get all OS categories
   */
  getCategories: async (): Promise<OSCategoryResponse[]> => {
    const response = await api.get<{ name: string; icon: string; count: number }[]>('/os/categories');
    return response.data.map((cat, index) => ({
      category: ['windows', 'linux', 'macos', 'bsd'][index] as OSCategory,
      name: cat.name,
      icon: cat.icon,
      count: cat.count,
    }));
  },

  /**
   * Get Linux subcategories
   */
  getLinuxSubcategories: async (): Promise<LinuxSubcategory[]> => {
    const response = await api.get<LinuxSubcategory[]>('/os/linux/subcategories');
    return response.data;
  },

  /**
   * Get OS by category
   */
  getByCategory: async (category: OSCategory, subcategory?: string): Promise<OSInfo[]> => {
    const params = subcategory ? { subcategory } : {};
    const response = await api.get<OSInfo[]>(`/os/${category}`, { params });
    return response.data;
  },

  /**
   * Search OS
   */
  search: async (query: string, category?: OSCategory): Promise<OSInfo[]> => {
    const params = category ? { query, category } : { query };
    const response = await api.get<OSInfo[]>('/os/search', { params });
    return response.data;
  },
};

/**
 * Downloads API
 */
export const downloadsAPI = {
  /**
   * Start a new download
   */
  start: async (osId: string, outputName?: string): Promise<DownloadStatus> => {
    const response = await api.post<DownloadStatus>('/downloads/start', {
      os_id: osId,
      output_name: outputName,
    });
    return response.data;
  },

  /**
   * Get all downloads
   */
  getAll: async (state?: string): Promise<DownloadStatus[]> => {
    const params = state ? { state } : {};
    const response = await api.get<DownloadStatus[]>('/downloads', { params });
    return response.data;
  },

  /**
   * Get specific download
   */
  get: async (downloadId: number): Promise<DownloadStatus> => {
    const response = await api.get<DownloadStatus>(`/downloads/${downloadId}`);
    return response.data;
  },

  /**
   * Pause a download
   */
  pause: async (downloadId: number): Promise<void> => {
    await api.post(`/downloads/${downloadId}/pause`);
  },

  /**
   * Resume a download
   */
  resume: async (downloadId: number): Promise<void> => {
    await api.post(`/downloads/${downloadId}/resume`);
  },

  /**
   * Cancel a download (keeps in database with cancelled state)
   */
  cancel: async (downloadId: number): Promise<void> => {
    await api.post(`/downloads/${downloadId}/cancel`);
  },

  /**
   * Delete/dismiss a download (removes from database)
   */
  delete: async (downloadId: number): Promise<void> => {
    await api.delete(`/downloads/${downloadId}`);
  },

  /**
   * Clear completed downloads
   */
  clearCompleted: async (): Promise<void> => {
    await api.delete('/downloads/completed');
  },

  /**
   * Get statistics
   */
  getStats: async (): Promise<Stats> => {
    const response = await api.get<Stats>('/downloads/stats');
    return response.data;
  },
};

/**
 * Health check
 */
export const healthAPI = {
  check: async (): Promise<{ status: string; service: string }> => {
    const response = await api.get('/health');
    return response.data;
  },
};
