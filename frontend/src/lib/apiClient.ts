/**
 * API Client with Auth Interceptor
 * Adheres to /frontend/INSTRUCTION.md line 49
 */

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || process.env.VITE_API_URL || 'http://localhost:8000';

export async function apiClient<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('docta_auth_token') : null;

  const headers: Record<string, string> = {
    Accept: 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...((options.headers as Record<string, string>) || {}),
  };

  if (!(options.body instanceof FormData) && options.body && typeof options.body === 'object') {
    headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(options.body);
  }

  const url = endpoint.startsWith('http') ? endpoint : `${BASE_URL}${endpoint}`;

  const res = await fetch(url, { ...options, headers });
  if (!res.ok) {
    const errorText = await res.text().catch(() => '');
    throw new Error(`API Error [${res.status}]: ${errorText || res.statusText}`);
  }

  return (await res.json()) as T;
}
