import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authAPI } from './api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const savedUser = localStorage.getItem('user');
    
    if (token && savedUser) {
      setUser(JSON.parse(savedUser));
    }
    setLoading(false);
  }, []);

  const login = useCallback(async (email, password) => {
    try {
      const response = await authAPI.login(email, password);
      const { access_token, user: userData } = response.data;
      
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));
      setUser(userData);
      
      return { ok: true, user: userData };
    } catch (error) {
      return {
        ok: false,
        message: error.response?.data?.detail || 'Ошибка входа'
      };
    }
  }, []);

  const register = useCallback(async (data) => {
    try {
      const response = await authAPI.register(data);
      const { access_token, user: userData } = response.data;
      
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));
      setUser(userData);
      
      return { ok: true, user: userData };
    } catch (error) {
      return {
        ok: false,
        message: error.response?.data?.email?.[0] || 'Ошибка регистрации'
      };
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    setUser(null);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <AuthContext.Provider value={{ user, login, register, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider');
  return ctx;
}
