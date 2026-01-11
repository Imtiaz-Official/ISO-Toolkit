/**
 * Comprehensive Admin Dashboard Page
 * Features: Analytics, ISO Management, User Management, Settings, Activity Logs
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

// API base URL
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

type TabType = 'overview' | 'isos' | 'users' | 'settings' | 'logs';

// Analytics interfaces
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

// System Health
interface SystemHealth {
  disk_usage_percent: number;
  disk_free_gb: number;
  disk_total_gb: number;
  memory_usage_percent: number;
  uptime_seconds: number;
}

// User interfaces
interface User {
  id: number;
  username: string;
  email: string;
  is_admin: boolean;
  is_active: boolean;
  created_at: string;
  last_login: string | null;
}

// ISO interfaces
interface ISO {
  id: string;
  name: string;
  version: string;
  category: string;
  architecture: string;
  language: string;
  url: string;
  size: number;
  description?: string;
  icon?: string;
  checksum?: string;
  checksum_type?: string;
  created_at?: string;
  is_custom?: boolean;
  can_edit?: boolean;
}

interface ISOCreate {
  name: string;
  version: string;
  category: string;
  architecture: string;
  language: string;
  url: string;
  size: number;
  description?: string;
  icon?: string;
  checksum?: string;
  checksum_type?: string;
}

// Activity Log interfaces
interface ActivityLog {
  id: string;
  timestamp: string;
  user: string;
  action: string;
  details: Record<string, any>;
  ip_address?: string;
}

// Settings interface
interface SystemSettings {
  site_name: string;
  site_description: string;
  allow_registration: boolean;
  max_download_size_gb: number;
  download_timeout_seconds: number;
  maintenance_mode: boolean;
  custom_css?: string;
  custom_js?: string;
}

const CATEGORIES = ['WINDOWS', 'LINUX', 'MACOS', 'BSD', 'OTHER'];
const ARCHITECTURES = ['X64', 'X86', 'ARM64', 'ARM', 'RISCV64', 'UNIVERSAL'];
const LANGUAGES = ['en', 'en-US', 'en-GB', 'de', 'fr', 'es', 'it', 'pt', 'ru', 'ja', 'ko', 'zh-CN'];
const CHECKSUM_TYPES = ['sha256', 'sha512', 'md5', 'sha1'];

const TOKEN_KEY = 'access_token';
const ACTIVE_TAB_KEY = 'admin_active_tab';

export default function AdminDashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  // Load active tab from localStorage on mount
  const [activeTab, setActiveTab] = useState<TabType>(() => {
    const saved = localStorage.getItem(ACTIVE_TAB_KEY);
    return (saved === 'overview' || saved === 'isos' || saved === 'users' || saved === 'settings' || saved === 'logs')
      ? saved as TabType
      : 'overview';
  });
  const [, setLoading] = useState(true);

  // Save active tab to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem(ACTIVE_TAB_KEY, activeTab);
  }, [activeTab]);

  // Redirect to change password if user hasn't changed their password
  useEffect(() => {
    if (user && !user.password_changed) {
      navigate('/admin/change-password', { replace: true });
    }
  }, [user, navigate]);

  // Overview data
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [dashboardData, setDashboardData] = useState<any>(null);

  // Users data
  const [users, setUsers] = useState<User[]>([]);
  const [usersLoading, setUsersLoading] = useState(false);

  // ISOs data
  const [isos, setISOs] = useState<ISO[]>([]);
  const [isosLoading, setISOLoading] = useState(false);
  const [isoStats, setISOStats] = useState<any>(null);
  const [showISOForm, setShowISOForm] = useState(false);
  const [editingISO, setEditingISO] = useState<ISO | null>(null);
  const [isoFormData, setISOFormData] = useState<ISOCreate>({
    name: '',
    version: '',
    category: 'LINUX',
    architecture: 'X64',
    language: 'en',
    url: '',
    size: 0,
    description: '',
    icon: '',
    checksum: '',
    checksum_type: 'sha256'
  });

  // Activity logs data
  const [activityLogs, setActivityLogs] = useState<ActivityLog[]>([]);
  const [logsLoading, setLogsLoading] = useState(false);

  // Settings data
  const [settings, setSettings] = useState<SystemSettings | null>(null);
  const [settingsLoading, setSettingsLoading] = useState(false);
  const [settingsFormData, setSettingsFormData] = useState<SystemSettings>({
    site_name: 'ISO Toolkit',
    site_description: 'Multi-OS ISO Downloader Toolkit',
    allow_registration: true,
    max_download_size_gb: 100,
    download_timeout_seconds: 3600,
    maintenance_mode: false
  });

  // Get auth headers
  const getAuthHeaders = () => {
    const token = localStorage.getItem(TOKEN_KEY);
    return {
      headers: { Authorization: `Bearer ${token}` }
    };
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  // Load data for the active tab on mount and when tab changes
  useEffect(() => {
    if (activeTab === 'users' && users.length === 0) fetchUsers();
    if (activeTab === 'isos' && isos.length === 0) {
      fetchISOs();
      fetchISOStats();
    }
    if (activeTab === 'logs' && activityLogs.length === 0) fetchActivityLogs();
    if (activeTab === 'settings' && !settings) fetchSettings();
  }, [activeTab]);

  const loadDashboardData = async () => {
    await Promise.all([
      fetchAnalytics(),
      fetchSystemHealth(),
      fetchDashboardOverview()
    ]);
    setLoading(false);
  };

  // Analytics fetchers
  const fetchAnalytics = async () => {
    try {
      const response = await axios.get(`${API_BASE}/analytics/detailed`, getAuthHeaders());
      setAnalytics(response.data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    }
  };

  const fetchSystemHealth = async () => {
    try {
      const response = await axios.get(`${API_BASE}/analytics/system-health`, getAuthHeaders());
      setSystemHealth(response.data);
    } catch (error) {
      console.error('Failed to fetch system health:', error);
    }
  };

  const fetchDashboardOverview = async () => {
    try {
      const response = await axios.get(`${API_BASE}/admin/dashboard`, getAuthHeaders());
      setDashboardData(response.data);
    } catch (error) {
      console.error('Failed to fetch dashboard overview:', error);
    }
  };

  // User management
  const fetchUsers = async () => {
    setUsersLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/auth/admin/users`, getAuthHeaders());
      setUsers(response.data);
    } catch (error) {
      console.error('Failed to fetch users:', error);
    } finally {
      setUsersLoading(false);
    }
  };

  const toggleAdmin = async (userId: number) => {
    try {
      await axios.post(`${API_BASE}/auth/admin/users/${userId}/toggle-admin`, {}, getAuthHeaders());
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
      await axios.delete(`${API_BASE}/auth/admin/users/${userId}`, getAuthHeaders());
      await fetchUsers();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to delete user');
    }
  };

  const createUser = async (userData: { username: string; email: string; password: string; is_admin: boolean }) => {
    try {
      await axios.post(`${API_BASE}/auth/register`, userData, getAuthHeaders());
      await fetchUsers();
      alert('User created successfully!');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to create user');
    }
  };

  // ISO management
  const fetchISOs = async (category?: string) => {
    setISOLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/admin/iso${category ? `?category=${category}` : ''}`, getAuthHeaders());
      setISOs(response.data);
    } catch (error) {
      console.error('Failed to fetch ISOs:', error);
    } finally {
      setISOLoading(false);
    }
  };

  const fetchISOStats = async () => {
    try {
      const response = await axios.get(`${API_BASE}/admin/iso/stats`, getAuthHeaders());
      setISOStats(response.data);
    } catch (error) {
      console.error('Failed to fetch ISO stats:', error);
    }
  };

  const handleCreateISO = async () => {
    try {
      await axios.post(`${API_BASE}/admin/iso`, isoFormData, getAuthHeaders());
      setShowISOForm(false);
      resetISOForm();
      await fetchISOs();
      await fetchISOStats();
      alert('ISO created successfully!');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to create ISO');
    }
  };

  const handleUpdateISO = async () => {
    if (!editingISO) return;
    try {
      await axios.put(`${API_BASE}/admin/iso/${editingISO.id}`, isoFormData, getAuthHeaders());
      setShowISOForm(false);
      setEditingISO(null);
      resetISOForm();
      await fetchISOs();
      alert('ISO updated successfully!');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to update ISO');
    }
  };

  const handleDeleteISO = async (isoId: string) => {
    if (!confirm('Are you sure you want to delete this ISO?')) return;
    try {
      await axios.delete(`${API_BASE}/admin/iso/${isoId}`, getAuthHeaders());
      await fetchISOs();
      await fetchISOStats();
      alert('ISO deleted successfully!');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to delete ISO');
    }
  };

  const editISOCustom = (iso: ISO) => {
    setEditingISO(iso);
    setISOFormData({
      name: iso.name,
      version: iso.version,
      category: iso.category,
      architecture: iso.architecture,
      language: iso.language,
      url: iso.url,
      size: iso.size,
      description: iso.description,
      icon: iso.icon,
      checksum: iso.checksum,
      checksum_type: iso.checksum_type
    });
    setShowISOForm(true);
  };

  const resetISOForm = () => {
    setISOFormData({
      name: '',
      version: '',
      category: 'LINUX',
      architecture: 'X64',
      language: 'en',
      url: '',
      size: 0,
      description: '',
      icon: '',
      checksum: '',
      checksum_type: 'sha256'
    });
    setEditingISO(null);
  };

  // Activity logs
  const fetchActivityLogs = async () => {
    setLogsLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/admin/logs?limit=100`, getAuthHeaders());
      setActivityLogs(response.data);
    } catch (error) {
      console.error('Failed to fetch activity logs:', error);
    } finally {
      setLogsLoading(false);
    }
  };

  // Settings
  const fetchSettings = async () => {
    setSettingsLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/admin/settings`, getAuthHeaders());
      setSettings(response.data);
      setSettingsFormData(response.data);
    } catch (error) {
      console.error('Failed to fetch settings:', error);
    } finally {
      setSettingsLoading(false);
    }
  };

  const handleSaveSettings = async () => {
    try {
      await axios.post(`${API_BASE}/admin/settings`, settingsFormData, getAuthHeaders());
      await fetchSettings();
      alert('Settings saved successfully!');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to save settings');
    }
  };

  const toggleMaintenance = async (mode: boolean) => {
    try {
      await axios.post(`${API_BASE}/admin/maintenance/${mode}`, {}, getAuthHeaders());
      await fetchSettings();
      alert(`Maintenance mode ${mode ? 'enabled' : 'disabled'}!`);
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to toggle maintenance mode');
    }
  };

  // Utility functions
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
      other: '💿'
    };
    return icons[category.toLowerCase()] || '💿';
  };

  // Tab change handler
  const handleTabChange = (tab: TabType) => {
    setActiveTab(tab);
    if (tab === 'users' && users.length === 0) fetchUsers();
    if (tab === 'isos' && isos.length === 0) {
      fetchISOs();
      fetchISOStats();
    }
    if (tab === 'logs' && activityLogs.length === 0) fetchActivityLogs();
    if (tab === 'settings' && !settings) fetchSettings();
  };

  return (
    <div className="flex min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Sidebar */}
      <div className="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">
        <div className="p-4">
          <div className="text-2xl mb-2">💿</div>
          <h1 className="text-xl font-bold text-gray-900 dark:text-white">ISO Toolkit</h1>
          <p className="text-sm text-gray-600 dark:text-gray-400">Admin Panel</p>
        </div>

        <nav className="flex-1 overflow-y-auto px-4 space-y-2">
          <button
            onClick={() => handleTabChange('overview')}
            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
              activeTab === 'overview'
                ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            <span>📊</span>
            <span>Overview</span>
          </button>

          <button
            onClick={() => handleTabChange('isos')}
            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
              activeTab === 'isos'
                ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            <span>💽</span>
            <span>ISO Management</span>
          </button>

          <button
            onClick={() => handleTabChange('users')}
            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
              activeTab === 'users'
                ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            <span>👥</span>
            <span>Users</span>
          </button>

          <button
            onClick={() => handleTabChange('settings')}
            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
              activeTab === 'settings'
                ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            <span>⚙️</span>
            <span>Settings</span>
          </button>

          <button
            onClick={() => handleTabChange('logs')}
            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
              activeTab === 'logs'
                ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            <span>📜</span>
            <span>Activity Logs</span>
          </button>
        </nav>

        <div className="p-4 border-t border-gray-200 dark:border-gray-700">
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
            Logged in as <span className="font-medium text-gray-900 dark:text-white">{user?.username}</span>
          </p>
          <button
            onClick={logout}
            className="w-full px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm"
          >
            Logout
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 p-8">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Dashboard Overview</h1>
              <p className="text-gray-600 dark:text-gray-400 mt-1">Welcome back, {user?.username}</p>
            </div>

            {/* Stats Grid */}
            {analytics && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Total Downloads</p>
                      <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">{analytics.total_downloads}</p>
                    </div>
                    <div className="text-4xl">📥</div>
                  </div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Active</p>
                      <p className="text-3xl font-bold text-blue-600 dark:text-blue-400 mt-2">{analytics.active_downloads}</p>
                    </div>
                    <div className="text-4xl">🔄</div>
                  </div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Users</p>
                      <p className="text-3xl font-bold text-green-600 dark:text-green-400 mt-2">{dashboardData?.users?.total || 0}</p>
                    </div>
                    <div className="text-4xl">👥</div>
                  </div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Total ISOs</p>
                      <p className="text-3xl font-bold text-purple-600 dark:text-purple-400 mt-2">{dashboardData?.custom_isos_count || 0}</p>
                    </div>
                    <div className="text-4xl">💿</div>
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
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Disk Usage</span>
                        <span className="text-sm text-gray-600 dark:text-gray-400">
                          {systemHealth.disk_free_gb.toFixed(1)} GB free
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
                    </div>

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
                            systemHealth.memory_usage_percent > 90 ? 'bg-red-500' : 'bg-blue-500'
                          }`}
                          style={{ width: `${systemHealth.memory_usage_percent}%` }}
                        ></div>
                      </div>
                    </div>

                    <div>
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">System Uptime</span>
                      <p className="text-lg font-bold text-gray-900 dark:text-white mt-1">
                        {formatUptime(systemHealth.uptime_seconds)}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Recent Activity */}
            {dashboardData?.recent_activity && dashboardData.recent_activity.length > 0 && (
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
                <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                  <h2 className="text-xl font-bold text-gray-900 dark:text-white">Recent Activity</h2>
                </div>
                <div className="p-6">
                  <div className="space-y-3">
                    {dashboardData.recent_activity.slice(0, 10).map((log: ActivityLog) => (
                      <div key={log.id} className="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-700 last:border-0">
                        <div>
                          <p className="text-sm font-medium text-gray-900 dark:text-white">
                            {log.user} - {log.action}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            {new Date(log.timestamp).toLocaleString()}
                          </p>
                        </div>
                        <span className="text-xs text-gray-500 dark:text-gray-400">
                          {log.ip_address || 'Unknown IP'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ISO Management Tab */}
        {activeTab === 'isos' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white">ISO Management</h1>
                <p className="text-gray-600 dark:text-gray-400 mt-1">Add, edit, and remove ISO download links</p>
              </div>
              <button
                onClick={() => {
                  resetISOForm();
                  setShowISOForm(true);
                }}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Add New ISO
              </button>
            </div>

            {/* ISO Stats */}
            {isoStats && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
                  <p className="text-sm text-gray-600 dark:text-gray-400">Total ISOs</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white mt-2">{isoStats.total_count}</p>
                </div>
                <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
                  <p className="text-sm text-gray-600 dark:text-gray-400">Custom ISOs</p>
                  <p className="text-2xl font-bold text-blue-600 dark:text-blue-400 mt-2">{isoStats.custom_count}</p>
                </div>
                <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
                  <p className="text-sm text-gray-600 dark:text-gray-400">Categories</p>
                  <p className="text-2xl font-bold text-purple-600 dark:text-purple-400 mt-2">{Object.keys(isoStats.by_category || {}).length}</p>
                </div>
              </div>
            )}

            {/* Category Filter */}
            <div className="flex space-x-2">
              <button
                onClick={() => fetchISOs()}
                className="px-4 py-2 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                All
              </button>
              {CATEGORIES.map(cat => (
                <button
                  key={cat}
                  onClick={() => fetchISOs(cat)}
                  className="px-4 py-2 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  {getCategoryIcon(cat)} {cat}
                </button>
              ))}
            </div>

            {/* ISO Form Modal */}
            {showISOForm && (
              <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                <div className="bg-white dark:bg-gray-800 rounded-xl p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                      {editingISO ? 'Edit ISO' : 'Add New ISO'}
                    </h2>
                    <button
                      onClick={() => {
                        setShowISOForm(false);
                        resetISOForm();
                      }}
                      className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
                    >
                      ✕
                    </button>
                  </div>

                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Name *</label>
                        <input
                          type="text"
                          value={isoFormData.name}
                          onChange={(e) => setISOFormData({ ...isoFormData, name: e.target.value })}
                          className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                          required
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Version *</label>
                        <input
                          type="text"
                          value={isoFormData.version}
                          onChange={(e) => setISOFormData({ ...isoFormData, version: e.target.value })}
                          className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                          required
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Category *</label>
                        <select
                          value={isoFormData.category}
                          onChange={(e) => setISOFormData({ ...isoFormData, category: e.target.value })}
                          className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        >
                          {CATEGORIES.map(cat => (
                            <option key={cat} value={cat}>{cat}</option>
                          ))}
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Architecture *</label>
                        <select
                          value={isoFormData.architecture}
                          onChange={(e) => setISOFormData({ ...isoFormData, architecture: e.target.value })}
                          className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        >
                          {ARCHITECTURES.map(arch => (
                            <option key={arch} value={arch}>{arch}</option>
                          ))}
                        </select>
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Language *</label>
                      <select
                        value={isoFormData.language}
                        onChange={(e) => setISOFormData({ ...isoFormData, language: e.target.value })}
                        className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      >
                        {LANGUAGES.map(lang => (
                          <option key={lang} value={lang}>{lang}</option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Download URL *</label>
                      <input
                        type="url"
                        value={isoFormData.url}
                        onChange={(e) => setISOFormData({ ...isoFormData, url: e.target.value })}
                        className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        required
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Size (bytes) *</label>
                        <input
                          type="number"
                          value={isoFormData.size}
                          onChange={(e) => setISOFormData({ ...isoFormData, size: parseInt(e.target.value) || 0 })}
                          className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                          required
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Icon (emoji)</label>
                        <input
                          type="text"
                          value={isoFormData.icon || ''}
                          onChange={(e) => setISOFormData({ ...isoFormData, icon: e.target.value })}
                          className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                          placeholder="💿"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Checksum</label>
                      <div className="flex space-x-2">
                        <input
                          type="text"
                          value={isoFormData.checksum || ''}
                          onChange={(e) => setISOFormData({ ...isoFormData, checksum: e.target.value })}
                          className="flex-1 px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                          placeholder="Checksum hash"
                        />
                        <select
                          value={isoFormData.checksum_type || 'sha256'}
                          onChange={(e) => setISOFormData({ ...isoFormData, checksum_type: e.target.value })}
                          className="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        >
                          {CHECKSUM_TYPES.map(type => (
                            <option key={type} value={type}>{type.toUpperCase()}</option>
                          ))}
                        </select>
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Description</label>
                      <textarea
                        value={isoFormData.description || ''}
                        onChange={(e) => setISOFormData({ ...isoFormData, description: e.target.value })}
                        className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        rows={3}
                      />
                    </div>

                    <div className="flex justify-end space-x-3 pt-4">
                      <button
                        onClick={() => {
                          setShowISOForm(false);
                          resetISOForm();
                        }}
                        className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={editingISO ? handleUpdateISO : handleCreateISO}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                      >
                        {editingISO ? 'Update ISO' : 'Create ISO'}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* ISO List */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="overflow-x-auto">
                {isosLoading ? (
                  <div className="p-8 text-center text-gray-500 dark:text-gray-400">Loading ISOs...</div>
                ) : isos.length === 0 ? (
                  <div className="p-8 text-center text-gray-500 dark:text-gray-400">No ISOs found</div>
                ) : (
                  <table className="w-full">
                    <thead className="bg-gray-50 dark:bg-gray-900">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Name</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Version</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Category</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Arch</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Size</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Type</th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                      {isos.map((iso) => (
                        <tr key={iso.id} className="hover:bg-gray-50 dark:hover:bg-gray-900">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <span className="text-xl mr-2">{iso.icon || getCategoryIcon(iso.category)}</span>
                              <span className="text-sm font-medium text-gray-900 dark:text-white">{iso.name}</span>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">{iso.version}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                            {getCategoryIcon(iso.category)} {iso.category}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">{iso.architecture}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">{formatBytes(iso.size)}</td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            {iso.is_custom ? (
                              <span className="px-2 py-1 text-xs font-semibold rounded-full bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300">
                                Override
                              </span>
                            ) : (
                              <span className="px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300">
                                Built-in
                              </span>
                            )}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                            <div className="flex justify-end space-x-2">
                              <button
                                onClick={() => editISOCustom(iso)}
                                className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
                              >
                                Edit
                              </button>
                              {iso.is_custom && (
                                <button
                                  onClick={() => handleDeleteISO(iso.id)}
                                  className="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300"
                                >
                                  Delete
                                </button>
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
          </div>
        )}

        {/* Users Tab */}
        {activeTab === 'users' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white">User Management</h1>
                <p className="text-gray-600 dark:text-gray-400 mt-1">Manage users and permissions</p>
              </div>
              <button
                onClick={() => {
                  const username = prompt('Enter username:');
                  const email = prompt('Enter email:');
                  const password = prompt('Enter password (must be 8+ chars with uppercase, lowercase, and digit):');
                  const is_admin = confirm('Should this user be an admin?');
                  if (username && email && password) {
                    createUser({ username, email, password, is_admin });
                  }
                }}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Add New User
              </button>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="overflow-x-auto">
                {usersLoading ? (
                  <div className="p-8 text-center text-gray-500 dark:text-gray-400">Loading users...</div>
                ) : users.length === 0 ? (
                  <div className="p-8 text-center text-gray-500 dark:text-gray-400">No users found</div>
                ) : (
                  <table className="w-full">
                    <thead className="bg-gray-50 dark:bg-gray-900">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">User</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Email</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Role</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Status</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Last Login</th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Actions</th>
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
                                <div className="text-sm font-medium text-gray-900 dark:text-white">{u.username}</div>
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">{u.email}</td>
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
                              {u.id === user?.id && <span className="text-gray-400 dark:text-gray-600">Current</span>}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Settings Tab */}
        {activeTab === 'settings' && (
          <div className="space-y-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">System Settings</h1>
              <p className="text-gray-600 dark:text-gray-400 mt-1">Configure application settings</p>
            </div>

            {settingsLoading ? (
              <div className="text-center text-gray-500 dark:text-gray-400">Loading settings...</div>
            ) : (
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
                <div className="p-6 space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Site Name</label>
                      <input
                        type="text"
                        value={settingsFormData.site_name}
                        onChange={(e) => setSettingsFormData({ ...settingsFormData, site_name: e.target.value })}
                        className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Site Description</label>
                      <input
                        type="text"
                        value={settingsFormData.site_description}
                        onChange={(e) => setSettingsFormData({ ...settingsFormData, site_description: e.target.value })}
                        className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Max Download Size (GB)</label>
                      <input
                        type="number"
                        value={settingsFormData.max_download_size_gb}
                        onChange={(e) => setSettingsFormData({ ...settingsFormData, max_download_size_gb: parseInt(e.target.value) || 100 })}
                        className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Download Timeout (seconds)</label>
                      <input
                        type="number"
                        value={settingsFormData.download_timeout_seconds}
                        onChange={(e) => setSettingsFormData({ ...settingsFormData, download_timeout_seconds: parseInt(e.target.value) || 3600 })}
                        className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      />
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">Allow Registration</p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">Allow new users to register</p>
                      </div>
                      <button
                        onClick={() => setSettingsFormData({ ...settingsFormData, allow_registration: !settingsFormData.allow_registration })}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                          settingsFormData.allow_registration ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'
                        }`}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                            settingsFormData.allow_registration ? 'translate-x-6' : 'translate-x-1'
                          }`}
                        />
                      </button>
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">Maintenance Mode</p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">Take the site offline for maintenance</p>
                      </div>
                      <button
                        onClick={() => setSettingsFormData({ ...settingsFormData, maintenance_mode: !settingsFormData.maintenance_mode })}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                          settingsFormData.maintenance_mode ? 'bg-red-600' : 'bg-gray-200 dark:bg-gray-700'
                        }`}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                            settingsFormData.maintenance_mode ? 'translate-x-6' : 'translate-x-1'
                          }`}
                        />
                      </button>
                    </div>
                  </div>

                  <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200 dark:border-gray-700">
                    <button
                      onClick={() => toggleMaintenance(!settingsFormData.maintenance_mode)}
                      className={`px-4 py-2 rounded-lg transition-colors ${
                        settingsFormData.maintenance_mode
                          ? 'bg-green-600 text-white hover:bg-green-700'
                          : 'bg-yellow-600 text-white hover:bg-yellow-700'
                      }`}
                    >
                      {settingsFormData.maintenance_mode ? 'Disable Maintenance' : 'Enable Maintenance'}
                    </button>
                    <button
                      onClick={handleSaveSettings}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      Save Settings
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* System Actions */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">System Actions</h2>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <button
                    onClick={async () => {
                      if (confirm('Create a backup of the database?')) {
                        try {
                          await axios.post(`${API_BASE}/admin/backup`, {}, getAuthHeaders());
                          alert('Backup created successfully!');
                        } catch (error: any) {
                          alert(error.response?.data?.detail || 'Failed to create backup');
                        }
                      }
                    }}
                    className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg text-left hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors"
                  >
                    <div className="text-2xl mb-2">💾</div>
                    <h3 className="font-medium text-gray-900 dark:text-white">Create Backup</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Backup the database</p>
                  </button>

                  <button
                    onClick={async () => {
                      if (confirm('Clear the application cache?')) {
                        try {
                          await axios.post(`${API_BASE}/admin/clear-cache`, {}, getAuthHeaders());
                          alert('Cache cleared successfully!');
                        } catch (error: any) {
                          alert(error.response?.data?.detail || 'Failed to clear cache');
                        }
                      }
                    }}
                    className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg text-left hover:bg-yellow-100 dark:hover:bg-yellow-900/30 transition-colors"
                  >
                    <div className="text-2xl mb-2">🧹</div>
                    <h3 className="font-medium text-gray-900 dark:text-white">Clear Cache</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Clear application cache</p>
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Activity Logs Tab */}
        {activeTab === 'logs' && (
          <div className="space-y-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Activity Logs</h1>
              <p className="text-gray-600 dark:text-gray-400 mt-1">Audit trail of admin actions</p>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="overflow-x-auto">
                {logsLoading ? (
                  <div className="p-8 text-center text-gray-500 dark:text-gray-400">Loading logs...</div>
                ) : activityLogs.length === 0 ? (
                  <div className="p-8 text-center text-gray-500 dark:text-gray-400">No activity logs found</div>
                ) : (
                  <table className="w-full">
                    <thead className="bg-gray-50 dark:bg-gray-900">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Timestamp</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">User</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Action</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Details</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">IP Address</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                      {activityLogs.map((log) => (
                        <tr key={log.id} className="hover:bg-gray-50 dark:hover:bg-gray-900">
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                            {new Date(log.timestamp).toLocaleString()}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                            {log.user}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                            {log.action}
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-600 dark:text-gray-400">
                            {JSON.stringify(log.details)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                            {log.ip_address || '-'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
