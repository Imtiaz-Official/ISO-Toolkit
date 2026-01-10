/**
 * Main App component with routing and mobile-responsive navigation.
 */

import { Routes, Route, Link, useLocation } from 'react-router-dom';
import { lazy, Suspense, useState, useEffect } from 'react';
import { AuthProvider, withAuth } from './contexts/AuthContext';

// Apply theme from localStorage or default to auto
function applyTheme() {
  const settings = localStorage.getItem('iso-toolkit-settings');
  const theme = settings ? JSON.parse(settings).theme : 'auto';

  const isDark = theme === 'dark' || (theme === 'auto' && window.matchMedia('(prefers-color-scheme: dark)').matches);
  const root = document.documentElement;

  if (isDark) {
    root.classList.add('dark');
  } else {
    root.classList.remove('dark');
  }
}

// Lazy load pages for better performance
const HomePage = lazy(() => import('./pages/Home'));
const BrowsePage = lazy(() => import('./pages/BrowseOS'));
const DownloadsPage = lazy(() => import('./pages/Downloads'));
const SettingsPage = lazy(() => import('./pages/Settings'));
const LoginPage = lazy(() => import('./pages/Login'));

// Load AdminDashboard and wrap with auth
const AdminDashboardPageLazy = lazy(() => import('./pages/AdminDashboard'));
const AdminDashboardPage = withAuth(AdminDashboardPageLazy, true);

function Navigation() {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const isActive = (path: string) => location.pathname === path;

  const navItems = [
    { path: '/', label: 'Home', icon: '🏠' },
    { path: '/browse', label: 'Browse', icon: '🔍' },
    { path: '/downloads', label: 'Downloads', icon: '📥' },
    { path: '/settings', label: 'Settings', icon: '⚙️' },
    { path: '/admin/login', label: 'Admin', icon: '🔐' },
  ];

  return (
    <header className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <span className="text-2xl">💿</span>
            <span className="text-xl font-bold text-gray-900 dark:text-white hidden sm:inline">
              ISO Toolkit
            </span>
            <span className="text-xl font-bold text-gray-900 dark:text-white sm:hidden">
              ISO
            </span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex space-x-2">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive(item.path)
                    ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                }`}
              >
                <span>{item.icon}</span>
                <span>{item.label}</span>
              </Link>
            ))}
          </nav>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
            aria-label="Toggle menu"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              {mobileMenuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden pb-4">
            <nav className="flex flex-col space-y-1">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`flex items-center space-x-3 px-4 py-3 rounded-lg text-base font-medium transition-colors ${
                    isActive(item.path)
                      ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                  }`}
                >
                  <span className="text-xl">{item.icon}</span>
                  <span>{item.label}</span>
                </Link>
              ))}
            </nav>
          </div>
        )}
      </div>
    </header>
  );
}

function App() {
  // Apply theme on mount and listen for system theme changes
  useEffect(() => {
    applyTheme();

    // Listen for system theme changes when in auto mode
    const settings = localStorage.getItem('iso-toolkit-settings');
    const theme = settings ? JSON.parse(settings).theme : 'auto';

    if (theme === 'auto') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const handleChange = () => applyTheme();
      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    }
  }, []);

  return (
    <AuthProvider>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex flex-col">
        <Navigation />

        {/* Main Content */}
        <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
          <Suspense
            fallback={
              <div className="flex items-center justify-center h-64">
                <div className="flex flex-col items-center space-y-4">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Loading...</p>
                </div>
              </div>
            }
          >
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/browse" element={<BrowsePage />} />
              <Route path="/downloads" element={<DownloadsPage />} />
              <Route path="/settings" element={<SettingsPage />} />
              <Route path="/admin/login" element={<LoginPage />} />
              <Route path="/admin/dashboard" element={<AdminDashboardPage />} />
            </Routes>
          </Suspense>
        </main>

        {/* Footer */}
        <footer className="mt-auto py-6 border-t border-gray-200 dark:border-gray-800">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <p className="text-center text-sm text-gray-500 dark:text-gray-400">
              💿 ISO Toolkit - Multi-OS ISO Downloader
            </p>
            <p className="text-center text-xs text-gray-400 dark:text-gray-500 mt-2">
              Available for Windows, Linux, macOS, and BSD
            </p>
          </div>
        </footer>
      </div>
    </AuthProvider>
  );
}

export default App;
