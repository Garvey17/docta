import { apiRequest } from './apiClient.js';
import { MOCK_USER } from '../data/mockData.js';
import { saveAuth, clearAuth } from '../store/authStore.js';

const USE_MOCK =
  (typeof import.meta !== 'undefined' && import.meta.env?.VITE_USE_MOCK === 'true') ||
  (typeof process !== 'undefined' && process.env?.VITE_USE_MOCK === 'true');

export async function loginUser(email, password) {
  if (USE_MOCK) {
    const mockToken = `jwt_mock_${Date.now()}`;
    const user = { ...MOCK_USER, email: email || MOCK_USER.email };
    saveAuth(mockToken, user);
    return { access_token: mockToken, user };
  }

  const data = await apiRequest('/api/v1/auth/login', {
    method: 'POST',
    body: { email, password },
  });

  if (data?.access_token) {
    saveAuth(data.access_token, data.user);
    return data;
  }
  throw new Error('Invalid authentication response from server');
}

export async function signupUser(name, email, password) {
  if (USE_MOCK) {
    const mockToken = `jwt_mock_${Date.now()}`;
    const user = { ...MOCK_USER, name, email };
    saveAuth(mockToken, user);
    return { access_token: mockToken, user };
  }

  const data = await apiRequest('/api/v1/auth/signup', {
    method: 'POST',
    body: { name, email, password },
  });

  if (data?.access_token) {
    saveAuth(data.access_token, data.user);
    return data;
  }
  throw new Error('Invalid signup response from server');
}

export async function fetchCurrentUser() {
  if (USE_MOCK) {
    return MOCK_USER;
  }
  return await apiRequest('/api/v1/auth/me');
}

export async function logoutUser() {
  if (!USE_MOCK) {
    try {
      await apiRequest('/api/v1/auth/logout', { method: 'POST' });
    } catch (e) {
      console.warn('Backend logout error:', e);
    }
  }
  clearAuth();
  return true;
}
