import { storage } from '../core/storage.js';

const API_BASE_URL = 'http://127.0.0.1:5000';

function buildHeaders(headers = {}, isJson = true) {
  const nextHeaders = { ...headers };
  const token = storage.getAccessToken();

  if (token && !nextHeaders.Authorization) {
    nextHeaders.Authorization = `Bearer ${token}`;
  }

  if (isJson && !nextHeaders['Content-Type'] && !['GET', 'DELETE'].includes(headers.method || '')) {
    nextHeaders['Content-Type'] = 'application/json';
  }

  if (isJson && !nextHeaders['Content-Type'] && headers.body !== undefined) {
    nextHeaders['Content-Type'] = 'application/json';
  }

  return nextHeaders;
}

function normalizeError(status, payload, fallbackMessage) {
  const errorBody = payload && typeof payload === 'object' && payload.error ? payload.error : {};
  const message = errorBody.message || fallbackMessage || 'Request failed';
  const error = new Error(message);
  error.status = status;
  error.code = errorBody.code || null;
  error.details = errorBody.details || null;
  error.payload = payload;
  return error;
}

async function parseJson(response) {
  const text = await response.text();
  if (!text) {
    return null;
  }

  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

async function request(path, options = {}, retry = true) {
  const url = `${API_BASE_URL}${path}`;
  const requestHeaders = buildHeaders({ ...(options.headers || {}), method: options.method }, options.body !== undefined);

  const response = await fetch(url, {
    ...options,
    headers: requestHeaders,
  });

  const payload = await parseJson(response);

  if (!response.ok) {
    const isAuthFailure = response.status === 401;
    const isRefreshRequest = path === '/api/auth/refresh';
    const isLoginRequest = path === '/api/auth/login';

    if (isAuthFailure && retry && !isRefreshRequest && !isLoginRequest) {
      const refreshed = await refreshAccessToken();
      if (refreshed) {
        return request(path, options, false);
      }
    }

    if (isRefreshRequest && isAuthFailure) {
      storage.clearAuth();
    }

    throw normalizeError(response.status, payload, 'Request failed');
  }

  return payload;
}

export const api = {
  get(path, params = {}) {
    const query = new URLSearchParams(Object.entries(params).filter(([, value]) => value !== undefined && value !== null && value !== '')).toString();
    const finalPath = query ? `${path}?${query}` : path;
    return request(finalPath, { method: 'GET' }, true);
  },

  post(path, body = {}) {
    return request(path, {
      method: 'POST',
      body: JSON.stringify(body),
    }, true);
  },

  put(path, body = {}) {
    return request(path, {
      method: 'PUT',
      body: JSON.stringify(body),
    }, true);
  },

  patch(path, body = {}) {
    return request(path, {
      method: 'PATCH',
      body: JSON.stringify(body),
    }, true);
  },

  delete(path, body = undefined) {
    return request(path, {
      method: 'DELETE',
      ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
    }, true);
  },

  async logout() {
    const refreshToken = storage.getRefreshToken();
    const accessToken = storage.getAccessToken();

    try {
      if (refreshToken && accessToken) {
        await request('/api/auth/logout', {
          method: 'POST',
          headers: { Authorization: `Bearer ${accessToken}` },
          body: JSON.stringify({ refresh_token: refreshToken }),
        }, true);
      }
    } catch {
      // Ignore logout failures and clear local state.
    }

    storage.clearAuth();
  },
};

export async function refreshAccessToken() {
  const refreshToken = storage.getRefreshToken();
  if (!refreshToken) return null;

  try {
    const result = await request('/api/auth/refresh', {
      method: 'POST',
      headers: { Authorization: `Bearer ${refreshToken}` },
    }, false);

    const nextToken = result?.data?.access_token;
    if (nextToken) {
      storage.setAccessToken(nextToken);
      return nextToken;
    }
  } catch {
    storage.clearAuth();
  }

  return null;
}
