/**
 * Settings page - Configure application settings.
 * Full redesign with modern UI and mobile responsive drawer.
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { downloadsAPI } from '../services/api';

type TabType = 'general' | 'downloads' | 'appearance' | 'advanced';

interface Settings {
  // General
  language: string;
  autoCheckUpdates: boolean;
  minimizeToTray: boolean;
  startMinimized: boolean;

  // Downloads
  downloadDirectory: string;
  maxConcurrentDownloads: number;
  maxDownloadSpeed: number;
  autoStartDownloads: boolean;
  verifyChecksums: boolean;
  deleteAfterInstall: boolean;
  lowPriorityMode: boolean;

  // Appearance
  theme: 'light' | 'dark' | 'auto';
  accentColor: string;
  fontSize: 'sm' | 'md' | 'lg';
  showFileSizes: boolean;
  compactMode: boolean;

  // Advanced
  enableProxy: boolean;
  proxyHost: string;
  proxyPort: string;
  enableLogging: boolean;
  logLevel: string;
}

const defaultSettings: Settings = {
  // General
  language: 'en-US',
  autoCheckUpdates: true,
  minimizeToTray: true,
  startMinimized: false,

  // Downloads
  downloadDirectory: 'C:\\Users\\Public\\Downloads\\ISOs',
  maxConcurrentDownloads: 3,
  maxDownloadSpeed: 0,
  autoStartDownloads: true,
  verifyChecksums: true,
  deleteAfterInstall: false,
  lowPriorityMode: false,

  // Appearance
  theme: 'auto',  // Auto-detects device theme (dark/light)
  accentColor: 'blue',
  fontSize: 'md',
  showFileSizes: true,
  compactMode: false,

  // Advanced
  enableProxy: false,
  proxyHost: '',
  proxyPort: '8080',
  enableLogging: true,
  logLevel: 'info',
};

const tabs: { id: TabType; name: string; icon: string }[] = [
  { id: 'general', name: 'General', icon: '⚙️' },
  { id: 'downloads', name: 'Downloads', icon: '📥' },
  { id: 'appearance', name: 'Appearance', icon: '🎨' },
  { id: 'advanced', name: 'Advanced', icon: '🔧' },
];

// Load settings from localStorage
function loadSettings(): Settings {
  const saved = localStorage.getItem('iso-toolkit-settings');
  if (saved) {
    try {
      return { ...defaultSettings, ...JSON.parse(saved) };
    } catch {
      return defaultSettings;
    }
  }
  return defaultSettings;
}

// Apply theme to document
function applyTheme(theme: 'light' | 'dark' | 'auto') {
  const root = document.documentElement;
  const isDark = theme === 'dark' || (theme === 'auto' && window.matchMedia('(prefers-color-scheme: dark)').matches);
  if (isDark) {
    root.classList.add('dark');
  } else {
    root.classList.remove('dark');
  }
}

// Apply accent color to CSS variables
function applyAccentColor(color: string) {
  const colors: Record<string, { r: number; g: number; b: number }> = {
    blue: { r: 59, g: 130, b: 246 },
    purple: { r: 168, g: 85, b: 247 },
    green: { r: 34, g: 197, b: 94 },
    red: { r: 239, g: 68, b: 68 },
    orange: { r: 249, g: 115, b: 22 },
    pink: { r: 236, g: 72, b: 153 },
  };

  const { r, g, b } = colors[color] || colors.blue;
  const root = document.documentElement;
  root.style.setProperty('--primary', `${r} ${g} ${b}`);
  root.style.setProperty('--ring', `${r} ${g} ${b}`);
}

// Apply font size to document
function applyFontSize(size: 'sm' | 'md' | 'lg') {
  const root = document.documentElement;
  const sizes = { sm: '13px', md: '16px', lg: '19px' };
  root.style.fontSize = sizes[size];
}

// Apply compact mode to document
function applyCompactMode(enabled: boolean) {
  const root = document.documentElement;
  if (enabled) {
    root.setAttribute('data-compact', 'true');
  } else {
    root.removeAttribute('data-compact');
  }
}

// Apply show file sizes to document
function applyShowFileSizes(enabled: boolean) {
  const root = document.documentElement;
  root.setAttribute('data-show-file-sizes', enabled.toString());
}

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<TabType>('general');
  const [settings, setSettings] = useState<Settings>(loadSettings);
  const [hasChanges, setHasChanges] = useState(false);

  // Apply appearance settings when they change
  useEffect(() => {
    applyTheme(settings.theme);
  }, [settings.theme]);

  useEffect(() => {
    applyAccentColor(settings.accentColor);
  }, [settings.accentColor]);

  useEffect(() => {
    applyFontSize(settings.fontSize);
  }, [settings.fontSize]);

  useEffect(() => {
    applyCompactMode(settings.compactMode);
  }, [settings.compactMode]);

  useEffect(() => {
    applyShowFileSizes(settings.showFileSizes);
  }, [settings.showFileSizes]);

  // Listen for system theme changes when in auto mode
  useEffect(() => {
    if (settings.theme === 'auto') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const handleChange = () => applyTheme('auto');
      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    }
  }, [settings.theme]);

  // Apply initial appearance settings on mount
  useEffect(() => {
    applyTheme(settings.theme);
    applyAccentColor(settings.accentColor);
    applyFontSize(settings.fontSize);
    applyCompactMode(settings.compactMode);
    applyShowFileSizes(settings.showFileSizes);
  }, []);

  function handleSave() {
    localStorage.setItem('iso-toolkit-settings', JSON.stringify(settings));
    console.log('Saving settings:', settings);
    setHasChanges(false);
    alert('Settings saved successfully!');
  }

  async function handleClearHistory() {
    if (!confirm('Are you sure you want to clear all completed, failed, and cancelled downloads? This cannot be undone.')) {
      return;
    }
    try {
      await downloadsAPI.clearCompleted();
      alert('Download history cleared successfully!');
    } catch (error) {
      console.error('Failed to clear history:', error);
      alert('Failed to clear download history. Please try again.');
    }
  }

  function handleReset() {
    const resetSettings = { ...defaultSettings, theme: settings.theme }; // Preserve theme
    setSettings(resetSettings);
    setHasChanges(true);
    // Apply reset appearance settings immediately
    applyAccentColor(resetSettings.accentColor);
    applyFontSize(resetSettings.fontSize);
    applyCompactMode(resetSettings.compactMode);
    applyShowFileSizes(resetSettings.showFileSizes);
  }

  function updateSetting<K extends keyof Settings>(key: K, value: Settings[K]) {
    setSettings({ ...settings, [key]: value });
    setHasChanges(true);

    // Apply appearance settings immediately for better UX
    if (key === 'theme') {
      applyTheme(value as 'light' | 'dark' | 'auto');
    } else if (key === 'accentColor') {
      applyAccentColor(value as string);
    } else if (key === 'fontSize') {
      applyFontSize(value as 'sm' | 'md' | 'lg');
    } else if (key === 'compactMode') {
      applyCompactMode(value as boolean);
    } else if (key === 'showFileSizes') {
      applyShowFileSizes(value as boolean);
    }
  }

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">Settings</h1>
          <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400 mt-1">Customize your experience</p>
        </div>
        <div className="flex flex-wrap gap-2 sm:gap-3">
          <Link to="/" className="btn btn-secondary text-sm sm:text-base">
            Back
          </Link>
          {hasChanges && (
            <>
              <button onClick={handleReset} className="btn btn-secondary text-sm sm:text-base">
                Reset
              </button>
              <button onClick={handleSave} className="btn btn-primary text-sm sm:text-base">
                Save Changes
              </button>
            </>
          )}
        </div>
      </div>

      {/* Mobile Tab Bar - Horizontal Scroll */}
      <div className="md:hidden overflow-x-auto -mx-4 px-4">
        <div className="flex space-x-2 pb-2">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 px-4 py-3 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
                activeTab === tab.id
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-700'
              }`}
            >
              <span className="text-lg">{tab.icon}</span>
              <span>{tab.name}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="flex flex-col md:flex-row gap-4 sm:gap-6">
        {/* Desktop Sidebar Navigation */}
        <div className="hidden md:block w-56 shrink-0">
          <nav className="card p-2 space-y-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-left transition-colors ${
                  activeTab === tab.id
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                }`}
              >
                <span className="text-xl">{tab.icon}</span>
                <span className="font-medium">{tab.name}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Settings Content */}
        <div className="flex-1 space-y-4 sm:space-y-6">
          {/* General Tab */}
          {activeTab === 'general' && (
            <>
              <section className="card p-4 sm:p-6 space-y-4 sm:space-y-6">
                <div className="flex items-center space-x-2 sm:space-x-3">
                  <span className="text-xl sm:text-2xl">🌐</span>
                  <h2 className="text-lg sm:text-xl font-semibold text-gray-900 dark:text-white">Language & Region</h2>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Language
                  </label>
                  <select
                    value={settings.language}
                    onChange={(e) => updateSetting('language', e.target.value)}
                    className="input"
                  >
                    <option value="en-US">English (United States)</option>
                    <option value="en-GB">English (United Kingdom)</option>
                    <option value="es-ES">Spanish (Spain)</option>
                    <option value="fr-FR">French (France)</option>
                    <option value="de-DE">German (Germany)</option>
                    <option value="zh-CN">Chinese (Simplified)</option>
                    <option value="ja-JP">Japanese</option>
                    <option value="pt-BR">Portuguese (Brazil)</option>
                  </select>
                </div>
              </section>

              <section className="card p-4 sm:p-6 space-y-4 sm:space-y-6">
                <div className="flex items-center space-x-2 sm:space-x-3">
                  <span className="text-xl sm:text-2xl">🚀</span>
                  <h2 className="text-lg sm:text-xl font-semibold text-gray-900 dark:text-white">Startup & Behavior</h2>
                </div>

                <div className="space-y-3 sm:space-y-4">
                  <div className="flex items-center justify-between gap-3">
                    <div className="min-w-0 flex-1">
                      <div className="font-medium text-sm sm:text-base text-gray-900 dark:text-white">Check for updates automatically</div>
                      <div className="text-xs sm:text-sm text-gray-500 dark:text-gray-400">Get notified about new versions</div>
                    </div>
                    <button
                      onClick={() => updateSetting('autoCheckUpdates', !settings.autoCheckUpdates)}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                        settings.autoCheckUpdates ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
                          settings.autoCheckUpdates ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-gray-900 dark:text-white">Minimize to tray</div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">Keep running in background when closed</div>
                    </div>
                    <button
                      onClick={() => updateSetting('minimizeToTray', !settings.minimizeToTray)}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                        settings.minimizeToTray ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
                          settings.minimizeToTray ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-gray-900 dark:text-white">Start minimized</div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">Launch application minimized to tray</div>
                    </div>
                    <button
                      onClick={() => updateSetting('startMinimized', !settings.startMinimized)}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                        settings.startMinimized ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
                          settings.startMinimized ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>
                </div>
              </section>
            </>
          )}

          {/* Downloads Tab */}
          {activeTab === 'downloads' && (
            <>
              <section className="card p-4 sm:p-6 space-y-4 sm:space-y-6">
                <div className="flex items-center space-x-2 sm:space-x-3">
                  <span className="text-xl sm:text-2xl">📁</span>
                  <h2 className="text-lg sm:text-xl font-semibold text-gray-900 dark:text-white">Download Location</h2>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Default Download Directory
                  </label>
                  <div className="flex flex-col sm:flex-row gap-2">
                    <input
                      type="text"
                      value={settings.downloadDirectory}
                      onChange={(e) => updateSetting('downloadDirectory', e.target.value)}
                      className="input flex-1 text-sm"
                      placeholder="Enter download path"
                    />
                    <button
                      onClick={() => {
                        const dir = prompt('Enter download directory path:', settings.downloadDirectory);
                        if (dir) updateSetting('downloadDirectory', dir);
                      }}
                      className="btn btn-secondary text-sm"
                    >
                      Browse
                    </button>
                  </div>
                  <p className="text-xs sm:text-sm text-gray-500 dark:text-gray-400 mt-2">
                    Downloaded ISO files will be saved to this location
                  </p>
                </div>
              </section>

              <section className="card p-4 sm:p-6 space-y-4 sm:space-y-6">
                <div className="flex items-center space-x-2 sm:space-x-3">
                  <span className="text-xl sm:text-2xl">⚡</span>
                  <h2 className="text-lg sm:text-xl font-semibold text-gray-900 dark:text-white">Download Limits</h2>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Max Concurrent Downloads
                  </label>
                  <select
                    value={settings.maxConcurrentDownloads}
                    onChange={(e) => updateSetting('maxConcurrentDownloads', parseInt(e.target.value))}
                    className="input"
                  >
                    <option value={1}>1 download</option>
                    <option value={2}>2 downloads</option>
                    <option value={3}>3 downloads</option>
                    <option value={5}>5 downloads</option>
                    <option value={10}>10 downloads</option>
                  </select>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                    Maximum number of simultaneous downloads
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Max Download Speed (MB/s)
                  </label>
                  <select
                    value={settings.maxDownloadSpeed}
                    onChange={(e) => updateSetting('maxDownloadSpeed', parseInt(e.target.value))}
                    className="input"
                  >
                    <option value={0}>Unlimited</option>
                    <option value={5}>5 MB/s</option>
                    <option value={10}>10 MB/s</option>
                    <option value={20}>20 MB/s</option>
                    <option value={50}>50 MB/s</option>
                  </select>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                    0 means unlimited speed
                  </p>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-gray-900 dark:text-white">Low Priority Mode</div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">Use less system resources</div>
                  </div>
                  <button
                    onClick={() => updateSetting('lowPriorityMode', !settings.lowPriorityMode)}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      settings.lowPriorityMode ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
                        settings.lowPriorityMode ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>
              </section>

              <section className="card p-4 sm:p-6 space-y-4 sm:space-y-6">
                <div className="flex items-center space-x-2 sm:space-x-3">
                  <span className="text-xl sm:text-2xl">🔧</span>
                  <h2 className="text-lg sm:text-xl font-semibold text-gray-900 dark:text-white">Download Behavior</h2>
                </div>

                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-gray-900 dark:text-white">Auto-start Downloads</div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">Automatically start downloads when added</div>
                    </div>
                    <button
                      onClick={() => updateSetting('autoStartDownloads', !settings.autoStartDownloads)}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                        settings.autoStartDownloads ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
                          settings.autoStartDownloads ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-gray-900 dark:text-white">Verify Checksums</div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">Verify ISO integrity after download</div>
                    </div>
                    <button
                      onClick={() => updateSetting('verifyChecksums', !settings.verifyChecksums)}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                        settings.verifyChecksums ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
                          settings.verifyChecksums ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-gray-900 dark:text-white">Delete after install</div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">Remove ISO after successful installation</div>
                    </div>
                    <button
                      onClick={() => updateSetting('deleteAfterInstall', !settings.deleteAfterInstall)}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                        settings.deleteAfterInstall ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
                          settings.deleteAfterInstall ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>
                </div>
              </section>
            </>
          )}

          {/* Appearance Tab */}
          {activeTab === 'appearance' && (
            <>
              <section className="card p-4 sm:p-6 space-y-4 sm:space-y-6">
                <div className="flex items-center space-x-2 sm:space-x-3">
                  <span className="text-xl sm:text-2xl">🎨</span>
                  <h2 className="text-lg sm:text-xl font-semibold text-gray-900 dark:text-white">Theme</h2>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                    App Theme
                  </label>
                  <div className="grid grid-cols-3 gap-3">
                    {(['light', 'dark', 'auto'] as const).map((theme) => (
                      <button
                        key={theme}
                        onClick={() => updateSetting('theme', theme)}
                        className={`p-4 rounded-lg border-2 transition-all ${
                          settings.theme === theme
                            ? 'border-blue-600 bg-blue-50 dark:bg-blue-900/20'
                            : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                        }`}
                      >
                        <div className="flex flex-col items-center space-y-2">
                          <div className={`w-12 h-12 rounded-lg ${theme === 'dark' ? 'bg-gray-900' : theme === 'light' ? 'bg-gray-100' : 'bg-gradient-to-r from-gray-100 to-gray-900'}`} />
                          <span className="font-medium capitalize text-gray-900 dark:text-white">{theme}</span>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                    Accent Color
                  </label>
                  <div className="flex space-x-2">
                    {[
                      { color: 'blue', bg: 'bg-blue-500' },
                      { color: 'purple', bg: 'bg-purple-500' },
                      { color: 'green', bg: 'bg-green-500' },
                      { color: 'red', bg: 'bg-red-500' },
                      { color: 'orange', bg: 'bg-orange-500' },
                      { color: 'pink', bg: 'bg-pink-500' },
                    ].map(({ color, bg }) => (
                      <button
                        key={color}
                        onClick={() => updateSetting('accentColor', color)}
                        className={`w-10 h-10 rounded-full ${bg} ${
                          settings.accentColor === color ? 'ring-2 ring-offset-2 ring-gray-900 dark:ring-white' : ''
                        }`}
                      />
                    ))}
                  </div>
                </div>
              </section>

              <section className="card p-4 sm:p-6 space-y-4 sm:space-y-6">
                <div className="flex items-center space-x-2 sm:space-x-3">
                  <span className="text-xl sm:text-2xl">📝</span>
                  <h2 className="text-lg sm:text-xl font-semibold text-gray-900 dark:text-white">Display</h2>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Font Size
                  </label>
                  <div className="flex space-x-2">
                    {(['sm', 'md', 'lg'] as const).map((size) => (
                      <button
                        key={size}
                        onClick={() => updateSetting('fontSize', size)}
                        className={`px-4 py-2 rounded-lg font-medium capitalize transition-colors ${
                          settings.fontSize === size
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                        }`}
                      >
                        {size === 'sm' ? 'Small' : size === 'md' ? 'Medium' : 'Large'}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-gray-900 dark:text-white">Show File Sizes</div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">Display file sizes in lists</div>
                    </div>
                    <button
                      onClick={() => updateSetting('showFileSizes', !settings.showFileSizes)}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                        settings.showFileSizes ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
                          settings.showFileSizes ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-gray-900 dark:text-white">Compact Mode</div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">Use smaller list items</div>
                    </div>
                    <button
                      onClick={() => updateSetting('compactMode', !settings.compactMode)}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                        settings.compactMode ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
                          settings.compactMode ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>
                </div>
              </section>
            </>
          )}

          {/* Advanced Tab */}
          {activeTab === 'advanced' && (
            <>
              <section className="card p-4 sm:p-6 space-y-4 sm:space-y-6">
                <div className="flex items-center space-x-2 sm:space-x-3">
                  <span className="text-xl sm:text-2xl">🌐</span>
                  <h2 className="text-lg sm:text-xl font-semibold text-gray-900 dark:text-white">Proxy Settings</h2>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-gray-900 dark:text-white">Enable Proxy</div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">Route downloads through proxy server</div>
                  </div>
                  <button
                    onClick={() => updateSetting('enableProxy', !settings.enableProxy)}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      settings.enableProxy ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
                        settings.enableProxy ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>

                {settings.enableProxy && (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Proxy Host
                      </label>
                      <input
                        type="text"
                        value={settings.proxyHost}
                        onChange={(e) => updateSetting('proxyHost', e.target.value)}
                        placeholder="127.0.0.1"
                        className="input"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Proxy Port
                      </label>
                      <input
                        type="text"
                        value={settings.proxyPort}
                        onChange={(e) => updateSetting('proxyPort', e.target.value)}
                        placeholder="8080"
                        className="input"
                      />
                    </div>
                  </div>
                )}
              </section>

              <section className="card p-4 sm:p-6 space-y-4 sm:space-y-6">
                <div className="flex items-center space-x-2 sm:space-x-3">
                  <span className="text-xl sm:text-2xl">📋</span>
                  <h2 className="text-lg sm:text-xl font-semibold text-gray-900 dark:text-white">Logging</h2>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-gray-900 dark:text-white">Enable Logging</div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">Log application activity for debugging</div>
                  </div>
                  <button
                    onClick={() => updateSetting('enableLogging', !settings.enableLogging)}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      settings.enableLogging ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
                        settings.enableLogging ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>

                {settings.enableLogging && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Log Level
                    </label>
                    <select
                      value={settings.logLevel}
                      onChange={(e) => updateSetting('logLevel', e.target.value)}
                      className="input"
                    >
                      <option value="debug">Debug</option>
                      <option value="info">Info</option>
                      <option value="warning">Warning</option>
                      <option value="error">Error</option>
                    </select>
                  </div>
                )}
              </section>

              <section className="card p-4 sm:p-6 space-y-4 sm:space-y-6 border-2 border-yellow-200 dark:border-yellow-900 bg-yellow-50 dark:bg-yellow-900/10">
                <div className="flex items-center space-x-2 sm:space-x-3">
                  <span className="text-xl sm:text-2xl">⚠️</span>
                  <h2 className="text-lg sm:text-xl font-semibold text-gray-900 dark:text-white">Danger Zone</h2>
                </div>

                <div className="space-y-4">
                  <div>
                    <h3 className="font-medium text-gray-900 dark:text-white mb-2">Clear Download History</h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">Remove all completed, failed, and cancelled downloads from history</p>
                    <button
                      onClick={handleClearHistory}
                      className="btn btn-secondary text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
                    >
                      Clear History
                    </button>
                  </div>

                  <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
                    <h3 className="font-medium text-gray-900 dark:text-white mb-2">Reset to Defaults</h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">Reset all settings to their default values</p>
                    <button onClick={handleReset} className="btn btn-secondary text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20">
                      Reset All Settings
                    </button>
                  </div>
                </div>
              </section>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
