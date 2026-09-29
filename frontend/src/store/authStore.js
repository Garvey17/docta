import { MOCK_USER } from '../data/mockData.js';

const TOKEN_KEY = 'docta_auth_token';
const USER_KEY = 'docta_auth_user';
const USE_MOCK = typeof import.meta !== 'undefined' && import.meta.env?.VITE_USE_MOCK === 'true';

export function getStoredAuth() {
  try {
    const token = localStorage.getItem(TOKEN_KEY);
    const userStr = localStorage.getItem(USER_KEY);
    if (token && userStr) {
      return { token, user: JSON.parse(userStr), isAuthenticated: true };
    }
  } catch (e) {
    console.error('Failed to read auth from localStorage', e);
  }

  if (USE_MOCK) {
    return { token: 'mock-jwt-token-docta-01', user: MOCK_USER, isAuthenticated: true };
  }

  return { token: null, user: null, isAuthenticated: false };
}

export function saveAuth(token, user) {
  try {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  } catch (e) {
    console.error('Failed to save auth to localStorage', e);
  }
}

export function clearAuth() {
  try {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  } catch (e) {
    console.error('Failed to clear auth from localStorage', e);
  }
}
