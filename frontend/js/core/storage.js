const TOKEN_KEY = 'domkg_access_token';
const REFRESH_KEY = 'domkg_refresh_token';
const USER_KEY = 'domkg_user';

export const storage = {
  getAccessToken() {
    return localStorage.getItem(TOKEN_KEY) || '';
  },

  setAccessToken(token) {
    if (!token) {
      localStorage.removeItem(TOKEN_KEY);
      return;
    }
    localStorage.setItem(TOKEN_KEY, token);
  },

  getRefreshToken() {
    return localStorage.getItem(REFRESH_KEY) || '';
  },

  setRefreshToken(token) {
    if (!token) {
      localStorage.removeItem(REFRESH_KEY);
      return;
    }
    localStorage.setItem(REFRESH_KEY, token);
  },

  getUser() {
    const raw = localStorage.getItem(USER_KEY);
    if (!raw) return null;
    try {
      return JSON.parse(raw);
    } catch {
      return null;
    }
  },

  setUser(user) {
    if (!user) {
      localStorage.removeItem(USER_KEY);
      return;
    }
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  },

  clearAuth() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
    localStorage.removeItem(USER_KEY);
  },
};
