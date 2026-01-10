/**
 * Home page - Landing page with quick stats and navigation.
 * Mobile responsive design.
 */

import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { downloadsAPI, osAPI } from '../services/api';
import type { Stats, OSCategory } from '../types';

export default function HomePage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [categories, setCategories] = useState<OSCategory[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [statsData, categoriesData] = await Promise.all([
          downloadsAPI.getStats(),
          osAPI.getCategories(),
        ]);
        setStats(statsData);
        setCategories(categoriesData);
      } catch (error) {
        console.error('Failed to load data:', error);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex flex-col items-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="text-sm text-gray-500 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 sm:space-y-8">
      {/* Hero Section */}
      <div className="text-center py-8 sm:py-12 px-4">
        <div className="flex justify-center mb-4">
          <span className="text-6xl sm:text-7xl">💿</span>
        </div>
        <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-900 dark:text-white mb-3 sm:mb-4">
          Welcome to ISO Toolkit
        </h1>
        <p className="text-base sm:text-xl text-gray-600 dark:text-gray-400 mb-6 sm:mb-8 max-w-2xl mx-auto px-4">
          Your multi-OS ISO downloader toolkit for Windows, Linux, macOS, and BSD
        </p>
        <div className="flex flex-col sm:flex-row justify-center items-center gap-3 sm:gap-4 px-4">
          <Link
            to="/browse"
            className="w-full sm:w-auto btn btn-primary text-center"
          >
            Browse ISOs
          </Link>
          <Link
            to="/downloads"
            className="w-full sm:w-auto btn btn-secondary text-center"
          >
            My Downloads
          </Link>
        </div>
      </div>

      {/* Stats Section */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-6">
          <div className="card text-center p-4 sm:p-6">
            <div className="text-xs sm:text-sm text-gray-500 dark:text-gray-400 mb-1">Total Downloads</div>
            <div className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">{stats.total_downloads}</div>
          </div>
          <div className="card text-center p-4 sm:p-6">
            <div className="text-xs sm:text-sm text-gray-500 dark:text-gray-400 mb-1">Active</div>
            <div className="text-2xl sm:text-3xl font-bold text-blue-600">{stats.active_downloads}</div>
          </div>
          <div className="card text-center p-4 sm:p-6">
            <div className="text-xs sm:text-sm text-gray-500 dark:text-gray-400 mb-1">Completed</div>
            <div className="text-2xl sm:text-3xl font-bold text-green-600">{stats.completed_downloads}</div>
          </div>
          <div className="card text-center p-4 sm:p-6">
            <div className="text-xs sm:text-sm text-gray-500 dark:text-gray-400 mb-1">Total Data</div>
            <div className="text-xl sm:text-3xl font-bold text-purple-600 truncate px-2">{stats.total_bytes_formatted}</div>
          </div>
        </div>
      )}

      {/* Categories Section */}
      {categories.length > 0 && (
        <div className="px-2 sm:px-0">
          <h2 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white mb-3 sm:mb-4 px-2">
            Available OS Categories
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
            {categories.map((category) => (
              <Link
                key={category.category}
                to={`/browse?category=${category.category}`}
                className="card hover:shadow-md transition-shadow cursor-pointer p-4 sm:p-6 text-center group"
              >
                <div className="text-4xl sm:text-5xl mb-2 sm:mb-3 group-hover:scale-110 transition-transform">
                  {category.icon}
                </div>
                <div className="font-semibold text-base sm:text-lg text-gray-900 dark:text-white">
                  {category.name}
                </div>
                <div className="text-xs sm:text-sm text-gray-500 dark:text-gray-400">
                  {category.count} ISOs available
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Quick Links */}
      <div className="px-2 sm:px-0">
        <h2 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white mb-3 sm:mb-4 px-2">
          Quick Links
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4">
          <Link
            to="/browse?category=windows"
            className="card hover:shadow-md transition-shadow p-4 sm:p-6 group"
          >
            <div className="flex items-center space-x-3 sm:space-x-4">
              <span className="text-3xl sm:text-4xl group-hover:scale-110 transition-transform">🪟</span>
              <div>
                <div className="font-semibold text-base sm:text-lg text-gray-900 dark:text-white">Windows ISOs</div>
                <div className="text-xs sm:text-sm text-gray-500 dark:text-gray-400">
                  Windows 11, 10, 8.1, 7, XP
                </div>
              </div>
            </div>
          </Link>
          <Link
            to="/browse?category=linux"
            className="card hover:shadow-md transition-shadow p-4 sm:p-6 group"
          >
            <div className="flex items-center space-x-3 sm:space-x-4">
              <span className="text-3xl sm:text-4xl group-hover:scale-110 transition-transform">🐧</span>
              <div>
                <div className="font-semibold text-base sm:text-lg text-gray-900 dark:text-white">Linux ISOs</div>
                <div className="text-xs sm:text-sm text-gray-500 dark:text-gray-400">
                  Ubuntu, Fedora, Debian, Mint, Arch
                </div>
              </div>
            </div>
          </Link>
          <Link
            to="/downloads"
            className="card hover:shadow-md transition-shadow p-4 sm:p-6 group"
          >
            <div className="flex items-center space-x-3 sm:space-x-4">
              <span className="text-3xl sm:text-4xl group-hover:scale-110 transition-transform">📥</span>
              <div>
                <div className="font-semibold text-base sm:text-lg text-gray-900 dark:text-white">Download Manager</div>
                <div className="text-xs sm:text-sm text-gray-500 dark:text-gray-400">
                  View and manage your downloads
                </div>
              </div>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
}
