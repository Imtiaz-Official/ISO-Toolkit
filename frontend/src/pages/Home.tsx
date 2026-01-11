/**
 * Home page - Landing page with animated hero and navigation.
 * Mobile responsive design with professional animations.
 */

import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { osAPI } from '../services/api';
import type { OSCategoryResponse } from '../types';

export default function HomePage() {
  const [categories, setCategories] = useState<OSCategoryResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const categoriesData = await osAPI.getCategories();
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

  // Floating icons animation data
  const floatingIcons = [
    { icon: '🪟', delay: 0, x: -10, y: -20 },
    { icon: '🐧', delay: 200, x: 20, y: -30 },
    { icon: '🍎', delay: 400, x: -25, y: 10 },
    { icon: '😈', delay: 600, x: 25, y: 20 },
    { icon: '📦', delay: 800, x: -15, y: 30 },
    { icon: '🔵', delay: 1000, x: 30, y: -10 },
    { icon: '💚', delay: 1200, x: -30, y: -15 },
    { icon: '🎩', delay: 1400, x: 10, y: 25 },
  ];

  return (
    <div className="space-y-6 sm:space-y-8">
      {/* Hero Section with Professional Animation */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-800 dark:via-gray-900 dark:to-black py-12 sm:py-20 px-4 sm:px-6">
        {/* Floating Icons Background Animation */}
        <div className="absolute inset-0 pointer-events-none overflow-hidden">
          {floatingIcons.map((item, index) => (
            <div
              key={index}
              className="absolute text-4xl sm:text-5xl opacity-20 dark:opacity-30 animate-float"
              style={{
                left: `${50 + item.x}%`,
                top: `${50 + item.y}%`,
                animationDelay: `${item.delay}ms`,
                animationDuration: `${3000 + index * 200}ms`,
              }}
            >
              {item.icon}
            </div>
          ))}
        </div>

        {/* Animated Gradient Orbs */}
        <div className="absolute top-0 left-1/4 w-64 sm:w-96 h-64 sm:h-96 bg-blue-400 dark:bg-blue-600 rounded-full mix-blend-multiply dark:mix-blend-soft-light filter blur-3xl opacity-30 dark:opacity-20 animate-pulse-slow"></div>
        <div className="absolute bottom-0 right-1/4 w-64 sm:w-96 h-64 sm:h-96 bg-purple-400 dark:bg-purple-600 rounded-full mix-blend-multiply dark:mix-blend-soft-light filter blur-3xl opacity-30 dark:opacity-20 animate-pulse-slow" style={{ animationDelay: '1s' }}></div>

        {/* Content */}
        <div className="relative z-10 text-center">
          {/* Animated ISO Icon */}
          <div className="flex justify-center mb-6">
            <div className="relative">
              <div className="absolute inset-0 bg-blue-500 dark:bg-blue-400 rounded-full blur-xl opacity-50 animate-pulse-slow"></div>
              <div className="relative text-7xl sm:text-8xl md:text-9xl animate-bounce-slow">
                💿
              </div>
            </div>
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-400 dark:to-purple-400 bg-clip-text text-transparent mb-4 sm:mb-6 animate-fade-in">
            ISO Toolkit
          </h1>

          <p className="text-lg sm:text-xl text-gray-700 dark:text-gray-300 mb-6 sm:mb-8 max-w-2xl mx-auto px-4 animate-fade-in" style={{ animationDelay: '200ms' }}>
            Your ultimate multi-OS ISO downloader toolkit
          </p>

          <div className="text-sm sm:text-base text-gray-600 dark:text-gray-400 mb-8 sm:mb-10 max-w-3xl mx-auto px-4 animate-fade-in" style={{ animationDelay: '400ms' }}>
            Download official Windows, Linux, macOS, and BSD ISO images with real-time progress tracking
          </div>

          <div className="flex flex-col sm:flex-row justify-center items-center gap-3 sm:gap-4 px-4 animate-fade-in" style={{ animationDelay: '600ms' }}>
            <Link
              to="/browse"
              className="w-full sm:w-auto px-6 sm:px-8 py-3 sm:py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 text-center"
            >
              Browse ISOs
            </Link>
            <Link
              to="/downloads"
              className="w-full sm:w-auto px-6 sm:px-8 py-3 sm:py-4 bg-white dark:bg-gray-800 text-gray-900 dark:text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 border border-gray-200 dark:border-gray-700 text-center"
            >
              My Downloads
            </Link>
          </div>

          {/* Feature Pills */}
          <div className="mt-8 sm:mt-12 flex flex-wrap justify-center gap-2 sm:gap-3 px-4 animate-fade-in" style={{ animationDelay: '800ms' }}>
            {[
              { text: '110+ Linux Distros', icon: '🐧' },
              { text: 'Windows 11/10', icon: '🪟' },
              { text: 'macOS Latest', icon: '🍎' },
              { text: 'BSD Family', icon: '😈' },
              { text: 'Resume Support', icon: '⬇️' },
              { text: 'Proxy Downloads', icon: '🔒' },
            ].map((feature, index) => (
              <div
                key={index}
                className="inline-flex items-center gap-2 px-3 sm:px-4 py-2 bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm rounded-full text-xs sm:text-sm text-gray-700 dark:text-gray-300 shadow-sm border border-gray-200 dark:border-gray-700"
              >
                <span>{feature.icon}</span>
                <span>{feature.text}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

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
