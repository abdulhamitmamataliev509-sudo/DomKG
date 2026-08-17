import { storage } from './storage.js';

class AuthState {
  constructor() {
    this.currentUser = storage.getUser();
    this.accessToken = storage.getAccessToken();
    this.refreshToken = storage.getRefreshToken();
    this.listeners = new Set();
  }

  subscribe(listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  emit() {
    this.listeners.forEach((listener) => listener(this.snapshot()));
  }

  snapshot() {
    return {
      currentUser: this.currentUser,
      accessToken: this.accessToken,
      refreshToken: this.refreshToken,
      isAuthenticated: Boolean(this.accessToken),
    };
  }

  setSession({ user, accessToken, refreshToken }) {
    this.currentUser = user || this.currentUser;
    this.accessToken = accessToken || this.accessToken;
    this.refreshToken = refreshToken || this.refreshToken;

    storage.setUser(this.currentUser);
    storage.setAccessToken(this.accessToken);
    storage.setRefreshToken(this.refreshToken);
    this.emit();
  }

  clearSession() {
    this.currentUser = null;
    this.accessToken = '';
    this.refreshToken = '';
    storage.clearAuth();
    this.emit();
  }
}

export const authState = new AuthState();
