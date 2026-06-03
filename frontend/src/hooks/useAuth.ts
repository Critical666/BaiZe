import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import type { UserInfo } from '@/api/auth';
import { getStoredUser } from '@/api/client';

export function useAuth() {
  const navigate = useNavigate();
  const [user, setUser] = useState<UserInfo | null>(getStoredUser);

  const setAuth = useCallback((token: string, userInfo: UserInfo) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(userInfo));
    setUser(userInfo);
  }, []);

  const clearAuth = useCallback(() => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    navigate('/login');
  }, [navigate]);

  const isAdmin = user?.role === 'admin';

  return { user, isAdmin, isLoggedIn: !!user, setAuth, clearAuth };
}
