const routes = new Map();

export function registerRoute(path, handler) {
  routes.set(path, handler);
}

export function navigateTo(path) {
  window.location.hash = path;
}

export function getCurrentRoute() {
  const hash = window.location.hash.replace(/^#/, '') || '/';
  const [pathname] = hash.split('?');
  return pathname || '/';
}

export function getCurrentQuery() {
  const hash = window.location.hash.replace(/^#/, '') || '/';
  const queryString = hash.includes('?') ? hash.split('?')[1] : '';
  return new URLSearchParams(queryString);
}

export function routeToPath(pathname) {
  const route = routes.get(pathname);
  if (route) return route;

  const match = [...routes.keys()].find((pattern) => {
    if (!pattern.includes(':')) return false;
    const patternParts = pattern.split('/');
    const urlParts = pathname.split('/');
    if (patternParts.length !== urlParts.length) return false;
    return patternParts.every((part, index) => part.startsWith(':') || part === urlParts[index]);
  });

  if (match) {
    return routes.get(match);
  }

  return routes.get('/not-found') || null;
}

export function initRouter() {
  const handleRoute = () => {
    const path = getCurrentRoute();
    const routeHandler = routeToPath(path);
    if (routeHandler) {
      routeHandler(path);
    }
  };

  window.addEventListener('hashchange', handleRoute);
  handleRoute();
}
