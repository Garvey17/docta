import { create } from 'zustand';
import { UserProfile } from '../types/api';
import { MOCK_USER } from '../lib/mockData';

interface AuthState {
  token: string | null;
  user: UserProfile | null;
  isAuthenticated: boolean;
  setAuth: (token: string, user: UserProfile) => void;
  clearAuth: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: typeof window !== 'undefined' ? localStorage.getItem('docta_auth_token') || 'mock-jwt-token' : 'mock-jwt-token',
  user: MOCK_USER,
  isAuthenticated: true,

  setAuth: (token: string, user: UserProfile) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('docta_auth_token', token);
      localStorage.setItem('docta_auth_user', JSON.stringify(user));
    }
    set({ token, user, isAuthenticated: true });
  },

  clearAuth: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('docta_auth_token');
      localStorage.removeItem('docta_auth_user');
    }
    set({ token: null, user: null, isAuthenticated: false });
  },
}));
