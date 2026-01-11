/**
 * Browse OS page - Browse and search for available OS ISOs.
 * Mobile responsive design with URL state persistence.
 */

import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { osAPI } from '../services/api';
import type { OSInfo, OSCategory, LinuxSubcategory } from '../types';
import { DistroLogo } from '../components/LogoImage';

// Simple emoji fallback map for common distros (used for subcategories to avoid loading 100+ SVGs)
const distroEmojis: Record<string, string> = {
  // Ubuntu Family
  'Ubuntu': '🟠',
  'Kubuntu': '💙',
  'Xubuntu': '🦊',
  'Lubuntu': '🐧',
  'Pop!_OS': '🚀',
  'Linux Mint': '🍃',
  'Linux Mint Cinnamon': '🍃',
  'Linux Mint MATE': '🍃',
  'Linux Mint XFCE': '🍃',
  'elementary OS': '💎',
  'Zorin OS': '🌟',
  'KDE neon': '💠',
  // Fedora & RHEL
  'Fedora': '🔵',
  'Rocky Linux': '💎',
  'AlmaLinux': '🐦',
  'CentOS Stream': '📦',
  'RHEL': '🎩',
  'Oracle Linux': '🔴',
  // Debian Family
  'Debian': '🔴',
  'Raspberry Pi OS': '🍓',
  // Arch Family
  'Arch Linux': '🏔️',
  'Manjaro': '💚',
  'EndeavourOS': '🚀',
  'Garuda Linux': '🦅',
  'Artix Linux': '🎨',
  'ArcoLinux': '🎯',
  // Others
  'Alpine Linux': '🏔️',
  'openSUSE': '🦎',
  'NixOS': '🌱',
  'Gentoo': '💜',
  'Void Linux': '⚫',
  'Slackware': '🔷',
  'Kali Linux': '🐉',
  'Parrot OS': '🦜',
  'Tails': '🕵️',
  'MX Linux': '🐴',
  'Solus': '🌿',
  'deepin': '🎨',
  'Puppy Linux': '🐕',
  'antiX': '🐜',
  'Bodhi Linux': '🌸',
  'Q4OS': '🔵',
  'PCLinuxOS': '🌲',
  'DietPi': '🥗',
  'LibreELEC': '📺',
  'Clear Linux': '💧',
  'Mageia': '🧙',
  'Amazon Linux': '📦',
  'BigLinux': '🇧🇷',
  'RebeccaBlackOS': '🎬',
  'Edubuntu': '🎓',
  'Ubuntu MATE': '💚',
  'Ubuntu Studio': '🎵',
  'Ubuntu Budgie': '🦜',
  'Ubuntu Cinnamon': '🎄',
  'Fedora ARM': '🔵',
};

// Get emoji for distro (fast, no external requests)
function getDistroEmoji(distroName: string): string {
  return distroEmojis[distroName] || '🐧';
}

// localStorage key for persisting last selected category
const LAST_CATEGORY_KEY = 'iso-toolkit-last-category';
const LAST_SUBCATEGORY_KEY = 'iso-toolkit-last-subcategory';

export default function BrowsePage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const categoryParam = searchParams.get('category');
  const subcategoryParam = searchParams.get('subcategory');

  // Get initial category from URL param, localStorage, or null
  const getInitialCategory = (): OSCategory | null => {
    if (categoryParam) return categoryParam as OSCategory;
    const saved = localStorage.getItem(LAST_CATEGORY_KEY);
    if (saved) return saved as OSCategory;
    return null;
  };

  const getInitialSubcategory = (): string | null => {
    if (subcategoryParam) return subcategoryParam;
    const saved = localStorage.getItem(LAST_SUBCATEGORY_KEY);
    if (saved) return saved;
    return null;
  };

  const [oss, setOss] = useState<OSInfo[]>([]);
  const [filteredOss, setFilteredOss] = useState<OSInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<OSCategory | null>(getInitialCategory);
  const [selectedSubcategory, setSelectedSubcategory] = useState<string | null>(getInitialSubcategory);
  const [linuxSubcategories, setLinuxSubcategories] = useState<LinuxSubcategory[]>([]);
  const [windowsSubcategories, setWindowsSubcategories] = useState<LinuxSubcategory[]>([]);
  const [loadingSubcategories, setLoadingSubcategories] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const categories: { value: OSCategory; name: string; icon: string }[] = [
    { value: 'windows', name: 'Windows', icon: '' },
    { value: 'linux', name: 'Linux', icon: '🐧' },
    { value: 'macos', name: 'macOS', icon: '🍎' },
    { value: 'bsd', name: 'BSD', icon: '🐡' },
  ];

  // Update URL params when category/subcategory changes
  useEffect(() => {
    const params = new URLSearchParams();
    if (selectedCategory) {
      params.set('category', selectedCategory);
    }
    if (selectedSubcategory) {
      params.set('subcategory', selectedSubcategory);
    }
    setSearchParams(params, { replace: true });
  }, [selectedCategory, selectedSubcategory, setSearchParams]);

  // Sync state with URL params on mount
  useEffect(() => {
    if (categoryParam && !selectedCategory) {
      setSelectedCategory(categoryParam as OSCategory);
    }
    if (subcategoryParam && !selectedSubcategory) {
      setSelectedSubcategory(subcategoryParam);
    }
  }, [categoryParam, subcategoryParam]);

  // Save selected category to localStorage whenever it changes
  useEffect(() => {
    if (selectedCategory) {
      localStorage.setItem(LAST_CATEGORY_KEY, selectedCategory);
    } else {
      localStorage.removeItem(LAST_CATEGORY_KEY);
    }
  }, [selectedCategory]);

  // Save selected subcategory to localStorage whenever it changes
  useEffect(() => {
    if (selectedSubcategory) {
      localStorage.setItem(LAST_SUBCATEGORY_KEY, selectedSubcategory);
    } else {
      localStorage.removeItem(LAST_SUBCATEGORY_KEY);
    }
  }, [selectedSubcategory]);

  // Load Linux/Windows subcategories when category is selected
  useEffect(() => {
    async function loadSubcategories() {
      if (selectedCategory === 'linux') {
        setLoadingSubcategories(true);
        try {
          const data = await osAPI.getLinuxSubcategories();
          setLinuxSubcategories(data);
          setWindowsSubcategories([]);
        } catch (error) {
          console.error('Failed to load Linux subcategories:', error);
        } finally {
          setLoadingSubcategories(false);
        }
      } else if (selectedCategory === 'windows') {
        setLoadingSubcategories(true);
        try {
          const data = await osAPI.getWindowsSubcategories();
          setWindowsSubcategories(data);
          setLinuxSubcategories([]);
        } catch (error) {
          console.error('Failed to load Windows subcategories:', error);
        } finally {
          setLoadingSubcategories(false);
        }
      } else {
        setLinuxSubcategories([]);
        setWindowsSubcategories([]);
        setSelectedSubcategory(null);
      }
    }
    loadSubcategories();
  }, [selectedCategory]);

  // Load OS when category or subcategory changes
  useEffect(() => {
    async function loadOS() {
      if (!selectedCategory) {
        setOss([]);
        setFilteredOss([]);
        setLoading(false);
        return;
      }

      // For Linux and Windows, require subcategory selection
      if ((selectedCategory === 'linux' || selectedCategory === 'windows') && !selectedSubcategory) {
        setOss([]);
        setFilteredOss([]);
        setLoading(false);
        return;
      }

      setLoading(true);
      try {
        const data = await osAPI.getByCategory(selectedCategory, selectedSubcategory || undefined);
        setOss(data);
        setFilteredOss(data);
      } catch (error) {
        console.error('Failed to load OS:', error);
      } finally {
        setLoading(false);
      }
    }
    loadOS();
  }, [selectedCategory, selectedSubcategory]);

  useEffect(() => {
    if (searchQuery.trim() === '') {
      setFilteredOss(oss);
    } else {
      const query = searchQuery.toLowerCase();
      const filtered = oss.filter(
        (os) =>
          os.name.toLowerCase().includes(query) ||
          os.version.toLowerCase().includes(query) ||
          os.description?.toLowerCase().includes(query)
      );
      setFilteredOss(filtered);
    }
  }, [searchQuery, oss]);

  function handleCategoryClick(category: OSCategory | null) {
    setSelectedCategory(category);
    setSelectedSubcategory(null);
  }

  function handleSubcategoryClick(subcategory: string | null) {
    setSelectedSubcategory(subcategory);
  }

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-2">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">Browse ISOs</h1>
          <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400 mt-1">
            Download Windows, Linux, macOS, and BSD
          </p>
        </div>
      </div>

      {/* Category Selector */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => handleCategoryClick(null)}
          className={`px-3 sm:px-4 py-2 rounded-lg font-medium text-sm sm:text-base transition-colors ${
            selectedCategory === null
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-700'
          }`}
        >
          All
        </button>
        {categories.map((cat) => (
          <button
            key={cat.value}
            onClick={() => handleCategoryClick(cat.value)}
            className={`px-3 sm:px-4 py-2 rounded-lg font-medium text-sm sm:text-base transition-colors ${
              selectedCategory === cat.value
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-700'
            }`}
          >
            <span className="hidden sm:inline">{cat.icon}</span> {cat.name}
          </button>
        ))}
      </div>

      {/* Linux Subcategory Selector */}
      {selectedCategory === 'linux' && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-base sm:text-lg font-semibold text-gray-900 dark:text-white">
              Select a Distribution
            </h2>
            <span className="text-xs sm:text-sm text-gray-500 dark:text-gray-400">
              {linuxSubcategories.length} distributions
            </span>
          </div>
          {loadingSubcategories ? (
            <div className="flex items-center justify-center h-20">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => handleSubcategoryClick(null)}
                className={`px-3 py-2 rounded-lg font-medium text-xs sm:text-sm transition-colors ${
                  selectedSubcategory === null
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-700'
                }`}
              >
                All Distributions
              </button>
              {linuxSubcategories.map((sub) => (
                <button
                  key={sub.subcategory}
                  onClick={() => handleSubcategoryClick(sub.subcategory)}
                  className={`px-2 sm:px-3 py-2 rounded-lg font-medium text-xs sm:text-sm transition-colors flex items-center gap-1 sm:gap-2 ${
                    selectedSubcategory === sub.subcategory
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-700'
                  }`}
                  title={`${sub.name} (${sub.count} ISOs)`}
                >
                  <span className="text-sm sm:text-base">{getDistroEmoji(sub.name)}</span>
                  <span className="hidden sm:inline">{sub.name}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Windows Subcategory Selector - Different Style (Cleaner, Fewer Options) */}
      {selectedCategory === 'windows' && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-base sm:text-lg font-semibold text-gray-900 dark:text-white">
              Select Windows Version
            </h2>
            <span className="text-xs sm:text-sm text-gray-500 dark:text-gray-400">
              {windowsSubcategories.length} versions
            </span>
          </div>
          {loadingSubcategories ? (
            <div className="flex items-center justify-center h-20">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2 sm:gap-3">
              {windowsSubcategories.map((sub) => (
                <button
                  key={sub.subcategory}
                  onClick={() => handleSubcategoryClick(sub.subcategory)}
                  className={`px-3 sm:px-4 py-3 sm:py-4 rounded-xl font-medium text-sm sm:text-base transition-all ${
                    selectedSubcategory === sub.subcategory
                      ? 'bg-blue-600 text-white shadow-lg scale-105'
                      : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                  }`}
                  title={`${sub.name} (${sub.count} ISOs)`}
                >
                  <div className="flex flex-col items-center gap-1 sm:gap-2">
                    <span className="text-xl sm:text-2xl">{sub.icon}</span>
                    <span className="text-xs sm:text-sm font-semibold">{sub.name}</span>
                    <span className="text-xs opacity-70">{sub.count} ISOs</span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Search */}
      <div className="relative">
        <input
          type="text"
          placeholder="Search ISOs..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="input pl-10 w-full"
          disabled={!selectedCategory || ((selectedCategory === 'linux' || selectedCategory === 'windows') && !selectedSubcategory)}
        />
        <svg
          className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center h-48">
          <div className="flex flex-col items-center space-y-3">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
            <p className="text-sm text-gray-500 dark:text-gray-400">Loading ISOs...</p>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!loading && selectedCategory === null && (
        <div className="text-center py-8 sm:py-12 px-4">
          <div className="text-5xl sm:text-6xl mb-4">💿</div>
          <h3 className="text-lg sm:text-xl font-semibold text-gray-900 dark:text-white mb-2">Select a Category</h3>
          <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400">Choose an OS category to browse available ISOs</p>
        </div>
      )}

      {/* No Results / Select Subcategory */}
      {!loading && selectedCategory && filteredOss.length === 0 && (
        <div className="text-center py-8 sm:py-12 px-4">
          {selectedCategory === 'linux' && !selectedSubcategory ? (
            <>
              <h3 className="text-lg sm:text-xl font-semibold text-gray-900 dark:text-white mb-2">Select a Distribution</h3>
              <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400">Choose a Linux distribution to browse available ISOs</p>
            </>
          ) : (
            <>
              <h3 className="text-lg sm:text-xl font-semibold text-gray-900 dark:text-white mb-2">No Results Found</h3>
              <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400">Try adjusting your search query</p>
            </>
          )}
        </div>
      )}

      {/* OS Grid - Mobile Responsive */}
      {!loading && filteredOss.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
          {filteredOss.map((os) => (
            <div key={os.id} className="card hover:shadow-md transition-shadow p-3 sm:p-4">
              {/* Header */}
              <div className="flex items-start justify-between mb-3 sm:mb-4">
                <div className="flex items-center space-x-2 sm:space-x-3">
                  {os.category === 'linux' ? (
                    <DistroLogo
                      distroName={os.subcategory || os.name}
                      size="lg"
                      className="shrink-0"
                    />
                  ) : (
                    <span className="text-2xl sm:text-3xl">{os.icon}</span>
                  )}
                  <div className="min-w-0">
                    <h3 className="font-semibold text-sm sm:text-lg text-gray-900 dark:text-white truncate">
                      {os.name}
                    </h3>
                    <p className="text-xs sm:text-sm text-gray-500 dark:text-gray-400 truncate">
                      {os.version}
                    </p>
                  </div>
                </div>
              </div>

              {/* Details */}
              <div className="space-y-1 sm:space-y-2 mb-3 sm:mb-4 text-xs sm:text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Arch:</span>
                  <span className="font-medium text-gray-900 dark:text-white">{os.architecture}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Language:</span>
                  <span className="font-medium text-gray-900 dark:text-white">{os.language}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Size:</span>
                  <span className="font-medium text-gray-900 dark:text-white">{os.size_formatted}</span>
                </div>
                <div className="hidden sm:flex items-center justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Source:</span>
                  <span className="font-medium text-gray-900 dark:text-white truncate ml-2">
                    {os.source || 'Unknown'}
                  </span>
                </div>
              </div>

              {/* Description */}
              {os.description && (
                <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mb-3 sm:mb-4 line-clamp-2 hidden sm:block">
                  {os.description}
                </p>
              )}

              {/* Actions */}
              <div className="flex flex-col sm:flex-row gap-2">
                <DownloadButton os={os} />
                <div className="flex gap-2">
                  <CopyLinkButton url={os.url} />
                  <a
                    href={os.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-secondary flex-1 flex items-center justify-center gap-1 text-xs sm:text-sm"
                    title="Open source"
                  >
                    <svg className="w-4 h-4 sm:w-4 sm:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                    <span className="hidden sm:inline">Source</span>
                  </a>
                </div>
              </div>

              {/* Checksum */}
              {os.checksum && (
                <div className="mt-2 sm:mt-3 text-[10px] sm:text-xs text-gray-500 dark:text-gray-400 truncate">
                  SHA256: {os.checksum.slice(0, 16)}...
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function DownloadButton({ os }: { os: OSInfo }) {
  // Direct download - redirects to ISO URL (like os.click)
  // Browser downloads directly from source, not through server
  return (
    <a
      href={`/api/downloads/direct/${os.id}`}
      className="btn btn-primary w-full sm:flex-1 text-sm sm:text-base inline-flex items-center justify-center"
      download
    >
      Download
    </a>
  );
}

function CopyLinkButton({ url }: { url: string }) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = url;
      textArea.style.position = 'fixed';
      textArea.style.opacity = '0';
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      try {
        document.execCommand('copy');
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      } catch (e) {
        console.error('Failed to copy:', e);
      }
      document.body.removeChild(textArea);
    }
  }

  return (
    <button
      onClick={handleCopy}
      className="btn btn-secondary flex-1 flex items-center justify-center gap-1 text-xs sm:text-sm"
      title="Copy download link"
    >
      {copied ? (
        <>
          <svg className="w-3 h-3 sm:w-4 sm:h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          <span className="hidden sm:inline">Copied!</span>
        </>
      ) : (
        <>
          <svg className="w-3 h-3 sm:w-4 sm:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
          <span className="hidden sm:inline">Copy</span>
        </>
      )}
    </button>
  );
}
