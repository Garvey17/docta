/**
 * HTTP Client with Auth Interceptor and Structured Error Handling
 */

function getBaseUrl() {
  return (
    (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_URL) ||
    (typeof process !== 'undefined' && process.env?.VITE_API_URL) ||
    'http://localhost:8000'
  );
}

export async function apiRequest(endpoint, options = {}) {
  const token = typeof localStorage !== 'undefined' ? localStorage.getItem('docta_auth_token') : null;
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

  const baseUrl = getBaseUrl();
  const url = endpoint.startsWith('http') ? endpoint : `${baseUrl}${endpoint}`;

  try {
    const res = await fetch(url, { ...options, headers });
    if (!res.ok) {
      const errorText = await res.text().catch(() => '');
      let detail = errorText;
      try {
        const parsed = JSON.parse(errorText);
        detail = parsed.detail || parsed.message || errorText;
      } catch {
        // use raw errorText
      }

      if (res.status === 401 && typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('docta:unauthorized'));
      }

      throw new Error(detail || `HTTP ${res.status}: ${res.statusText}`);
    }

    // Handle 204 No Content
    if (res.status === 204 || res.headers.get('content-length') === '0') {
      return null;
    }

    const contentType = res.headers.get('content-type') || '';
    if (contentType.includes('application/json')) {
      return await res.json();
    }
    if (contentType.includes('text/') || contentType.includes('csv')) {
      return await res.text();
    }
    return await res.blob();
  } catch (error) {
    // Propagate error to caller for honest UI error handling
    throw error;
  }
}
