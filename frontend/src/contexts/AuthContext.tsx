/**
 * Authentication Context for managing user authentication state.
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';

// API base URL
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface User {
  id: number;
  username: string;
  email: string;
  is_admin: boolean;
  is_active: boolean;
  created_at: string;
  last_login: string | null;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isAdmin: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
  checkAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Store tokens in localStorage
const TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Configure axios to include auth token
  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
  }, []);

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem(TOKEN_KEY);
      if (!token) {
        setUser(null);
        return;
      }

      const response = await axios.get(`${API_BASE}/api/auth/me`);
      setUser(response.data);
    } catch (error) {
      console.error('Auth check failed:', error);
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(REFRESH_TOKEN_KEY);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (username: string, password: string) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    try {
      const response = await axios.post(`${API_BASE}/api/auth/login`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const { access_token, refresh_token, user } = response.data;

      localStorage.setItem(TOKEN_KEY, access_token);
      localStorage.setItem(REFRESH_TOKEN_KEY, refresh_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

      setUser(user);
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Login failed';
      throw new Error(message);
    }
  };

  const logout = () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
  };

  const refreshToken = async () => {
    const refresh_token = localStorage.getItem(REFRESH_TOKEN_KEY);
    if (!refresh_token) {
      logout();
      return;
    }

    try {
      const response = await axios.post(`${API_BASE}/api/auth/refresh`, {
        refresh_token,
      });

      const { access_token, refresh_token: new_refresh_token, user } = response.data;

      localStorage.setItem(TOKEN_KEY, access_token);
      localStorage.setItem(REFRESH_TOKEN_KEY, new_refresh_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

      setUser(user);
    } catch (error) {
      console.error('Token refresh failed:', error);
      logout();
    }
  };

  useEffect(() => {
    checkAuth();
  }, []);

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isAdmin: user?.is_admin || false,
    isLoading,
    login,
    logout,
    refreshToken,
    checkAuth,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

// Higher-order component for protecting routes
export function withAuth<P extends object>(
  Component: React.ComponentType<P>,
  requireAdmin: boolean = false
) {
  return function AuthenticatedComponent(props: P) {
    const { isAuthenticated, isAdmin, isLoading } = useAuth();

    if (isLoading) {
      return (
        <div className="flex items-center justify-center h-64">
          <div className="flex flex-col items-center space-y-4">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="text-sm text-gray-500 dark:text-gray-400">Loading...</p>
          </div>
        </div>
      );
    }

    if (!isAuthenticated) {
      return (
        <div className="flex flex-col items-center justify-center h-96 space-y-4">
          <div className="text-6xl">🔒</div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Authentication Required</h2>
          <p className="text-gray-600 dark:text-gray-400">Please login to access this page.</p>
          <a
            href="/admin/login"
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Go to Login
          </a>
        </div>
      );
    }

    if (requireAdmin && !isAdmin) {
      return (
        <div className="flex flex-col items-center justify-center h-96 space-y-4">
          <div className="text-6xl">🚫</div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Admin Access Required</h2>
          <p className="text-gray-600 dark:text-gray-400">You don't have permission to access this page.</p>
        </div>
      );
    }

    return <Component {...props} />;
  };
}
