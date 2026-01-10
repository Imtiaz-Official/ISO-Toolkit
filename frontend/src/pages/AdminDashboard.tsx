/**
 * Admin Dashboard Page with enhanced analytics
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

// API base URL
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Analytics {
  total_downloads: number;
  active_downloads: number;
  completed_downloads: number;
  failed_downloads: number;
  total_bytes: number;
  category_breakdown: CategoryStats[];
  architecture_breakdown: ArchitectureStats[];
  recent_downloads: RecentDownload[];
  time_series_last_7_days: TimeSeriesData[];
  top_downloaded_os: TopOS[];
}

interface CategoryStats {
  category: string;
  count: number;
  total_bytes: number;
}

interface ArchitectureStats {
  architecture: string;
  count: number;
}

interface RecentDownload {
  id: number;
  os_name: string;
  os_version: string;
  os_category: string;
  state: string;
  created_at: string;
}

interface TimeSeriesData {
  date: string;
  count: number;
  total_bytes: number;
}

interface TopOS {
  name: string;
  version: string;
  count: number;
}

interface SystemHealth {
  disk_usage_percent: number;
  disk_free_gb: number;
  disk_total_gb: number;
  memory_usage_percent: number;
  uptime_seconds: number;
}

interface User {
  id: number;
  username: string;
  email: string;
  is_admin: boolean;
  is_active: boolean;
  created_at: string;
  last_login: string | null;
}

export default function AdminDashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
    fetchSystemHealth();
    fetchUsers();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/analytics/detailed`);
      setAnalytics(response.data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    }
  };

  const fetchSystemHealth = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/analytics/system-health`);
      setSystemHealth(response.data);
    } catch (error) {
      console.error('Failed to fetch system health:', error);
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/auth/admin/users`);
      setUsers(response.data);
    } catch (error) {
      console.error('Failed to fetch users:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleAdmin = async (userId: number) => {
    try {
      await axios.post(`${API_BASE}/api/auth/admin/users/${userId}/toggle-admin`);
      await fetchUsers();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to toggle admin status');
    }
  };

  const deleteUser = async (userId: number, username: string) => {
    if (!confirm(`Are you sure you want to delete user "${username}"?`)) {
      return;
    }
    try {
      await axios.delete(`${API_BASE}/api/auth/admin/users/${userId}`);
      await fetchUsers();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to delete user');
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${days}d ${hours}h ${minutes}m`;
  };

  const getCategoryIcon = (category: string) => {
    const icons: Record<string, string> = {
      windows: '🪟',
      linux: '🐧',
      macos: '🍎',
      bsd: '😈',
    };
    return icons[category.toLowerCase()] || '💿';
  };

  const getStateColor = (state: string) => {
    const colors: Record<string, string> = {
      completed: 'text-green-600',
      downloading: 'text-blue-600',
      failed: 'text-red-600',
      paused: 'text-yellow-600',
      pending: 'text-gray-600',
    };
    return colors[state.toLowerCase()] || 'text-gray-600';
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Admin Dashboard</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Welcome back, {user?.username}
          </p>
        </div>
        <button
          onClick={logout}
          className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          Logout
        </button>
      </div>

      {/* Stats Grid */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Downloads</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">
                  {analytics.total_downloads}
                </p>
              </div>
              <div className="text-4xl">📥</div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Active</p>
                <p className="text-3xl font-bold text-blue-600 dark:text-blue-400 mt-2">
                  {analytics.active_downloads}
                </p>
              </div>
              <div className="text-4xl">🔄</div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Completed</p>
                <p className="text-3xl font-bold text-green-600 dark:text-green-400 mt-2">
                  {analytics.completed_downloads}
                </p>
              </div>
              <div className="text-4xl">✅</div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Data</p>
                <p className="text-xl font-bold text-purple-600 dark:text-purple-400 mt-2">
                  {formatBytes(analytics.total_bytes)}
                </p>
              </div>
              <div className="text-4xl">💾</div>
            </div>
          </div>
        </div>
      )}

      {/* Analytics Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Breakdown */}
        {analytics && analytics.category_breakdown.length > 0 && (
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">Downloads by Category</h2>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {analytics.category_breakdown.map((cat) => (
                  <div key={cat.category} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl">{getCategoryIcon(cat.category)}</span>
                      <span className="font-medium text-gray-900 dark:text-white capitalize">
                        {cat.category}
                      </span>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-bold text-gray-900 dark:text-white">{cat.count}</div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        {formatBytes(cat.total_bytes)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* System Health */}
        {systemHealth && (
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">System Health</h2>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {/* Disk Usage */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Disk Usage</span>
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      {systemHealth.disk_free_gb.toFixed(1)} GB free of {systemHealth.disk_total_gb.toFixed(1)} GB
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        systemHealth.disk_usage_percent > 90
                          ? 'bg-red-500'
                          : systemHealth.disk_usage_percent > 70
                          ? 'bg-yellow-500'
                          : 'bg-green-500'
                      }`}
                      style={{ width: `${systemHealth.disk_usage_percent}%` }}
                    ></div>
                  </div>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    {systemHealth.disk_usage_percent.toFixed(1)}% used
                  </p>
                </div>

                {/* Memory Usage */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Memory Usage</span>
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      {systemHealth.memory_usage_percent.toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        systemHealth.memory_usage_percent > 90
                          ? 'bg-red-500'
                          : systemHealth.memory_usage_percent > 70
                          ? 'bg-yellow-500'
                          : 'bg-blue-500'
                      }`}
                      style={{ width: `${systemHealth.memory_usage_percent}%` }}
                    ></div>
                  </div>
                </div>

                {/* Uptime */}
                <div className="flex items-center justify-between pt-2">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">System Uptime</span>
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    {formatUptime(systemHealth.uptime_seconds)}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Top Downloaded OS */}
      {analytics && analytics.top_downloaded_os.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">Top Downloaded OS</h2>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              {analytics.top_downloaded_os.map((os, index) => (
                <div
                  key={`${os.name}-${os.version}`}
                  className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 text-center"
                >
                  <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                    #{index + 1}
                  </div>
                  <div className="text-sm font-medium text-gray-900 dark:text-white mt-2">
                    {os.name}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    {os.version}
                  </div>
                  <div className="text-lg font-bold text-gray-700 dark:text-gray-300 mt-2">
                    {os.count} <span className="text-sm font-normal">downloads</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Users Table */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">User Management</h2>
        </div>
        <div className="overflow-x-auto">
          {loading ? (
            <div className="p-8 text-center text-gray-500 dark:text-gray-400">Loading users...</div>
          ) : users.length === 0 ? (
            <div className="p-8 text-center text-gray-500 dark:text-gray-400">No users found</div>
          ) : (
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-900">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    User
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Email
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Role
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Last Login
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {users.map((u) => (
                  <tr key={u.id} className="hover:bg-gray-50 dark:hover:bg-gray-900">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold">
                          {u.username[0].toUpperCase()}
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900 dark:text-white">
                            {u.username}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                      {u.email}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {u.is_admin ? (
                        <span className="px-2 py-1 text-xs font-semibold rounded-full bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300">
                          Admin
                        </span>
                      ) : (
                        <span className="px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300">
                          User
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {u.is_active ? (
                        <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300">
                          Active
                        </span>
                      ) : (
                        <span className="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300">
                          Inactive
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                      {u.last_login ? new Date(u.last_login).toLocaleString() : 'Never'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                      <div className="flex justify-end space-x-2">
                        {u.id !== user?.id && (
                          <>
                            <button
                              onClick={() => toggleAdmin(u.id)}
                              className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
                            >
                              {u.is_admin ? 'Remove Admin' : 'Make Admin'}
                            </button>
                            <button
                              onClick={() => deleteUser(u.id, u.username)}
                              className="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300"
                            >
                              Delete
                            </button>
                          </>
                        )}
                        {u.id === user?.id && (
                          <span className="text-gray-400 dark:text-gray-600">Current</span>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Recent Downloads */}
      {analytics && analytics.recent_downloads.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">Recent Downloads</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-900">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    OS
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    Version
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    Category
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    Date
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {analytics.recent_downloads.map((dl) => (
                  <tr key={dl.id} className="hover:bg-gray-50 dark:hover:bg-gray-900">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                      {dl.os_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                      {dl.os_version}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                      {getCategoryIcon(dl.os_category)} {dl.os_category}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={getStateColor(dl.state)} capitalize">{dl.state}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                      {dl.created_at ? new Date(dl.created_at).toLocaleString() : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => navigate('/downloads')}
            className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg text-left hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors"
          >
            <div className="text-2xl mb-2">📥</div>
            <h3 className="font-medium text-gray-900 dark:text-white">Manage Downloads</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">View and manage active downloads</p>
          </button>
          <button
            onClick={() => navigate('/settings')}
            className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg text-left hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors"
          >
            <div className="text-2xl mb-2">⚙️</div>
            <h3 className="font-medium text-gray-900 dark:text-white">Settings</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">Configure application settings</p>
          </button>
          <button
            onClick={() => navigate('/browse')}
            className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg text-left hover:bg-purple-100 dark:hover:bg-purple-900/30 transition-colors"
          >
            <div className="text-2xl mb-2">🔍</div>
            <h3 className="font-medium text-gray-900 dark:text-white">Browse ISOs</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">Browse available ISO images</p>
          </button>
        </div>
      </div>
    </div>
  );
}
