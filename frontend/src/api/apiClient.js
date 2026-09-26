/**
 * HTTP Client with Auth Interceptor and Automatic Mock Fallback Support
 */

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function apiRequest(endpoint, options = {}) {
  const token = localStorage.getItem('docta_auth_token');
  const headers = {
    Accept: 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };

  // If body is FormData, do not set Content-Type (browser sets multipart boundary)
  if (!(options.body instanceof FormData) && options.body && typeof options.body === 'object') {
    headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(options.body);
  }

  const url = endpoint.startsWith('http') ? endpoint : `${BASE_URL}${endpoint}`;

  try {
    const res = await fetch(url, { ...options, headers });
    if (!res.ok) {
      const errorText = await res.text().catch(() => '');
      throw new Error(`API Error [${res.status}]: ${errorText || res.statusText}`);
    }
    return await res.json();
  } catch (error) {
    console.warn(`Request to ${endpoint} failed, falling back to client logic:`, error.message);
    throw error;
  }
}
