import { apiRequest } from './apiClient';
import { MOCK_USER } from '../data/mockData';
import { saveAuth } from '../store/authStore';

export async function loginUser(email, password) {
  try {
    const data = await apiRequest('/api/v1/auth/login', {
      method: 'POST',
      body: { email, password },
    });
    if (data?.access_token) {
      saveAuth(data.access_token, data.user || MOCK_USER);
      return data;
    }
  } catch (err) {
    console.warn('Backend auth offline, using demo profile');
  }

  const mockToken = `jwt_mock_${Date.now()}`;
  const user = { ...MOCK_USER, email: email || MOCK_USER.email };
  saveAuth(mockToken, user);
  return { access_token: mockToken, user };
}

export async function signupUser(name, email, password) {
  try {
    const data = await apiRequest('/api/v1/auth/signup', {
      method: 'POST',
      body: { name, email, password },
    });
    if (data?.access_token) {
      saveAuth(data.access_token, data.user || { ...MOCK_USER, name, email });
      return data;
    }
  } catch (err) {
    console.warn('Backend signup offline, using local mock account');
  }

  const mockToken = `jwt_mock_${Date.now()}`;
  const user = { ...MOCK_USER, name, email };
  saveAuth(mockToken, user);
  return { access_token: mockToken, user };
}
