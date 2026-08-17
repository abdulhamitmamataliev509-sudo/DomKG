import { api } from '../api/api.js';
import { authState } from './state.js';
import { getCurrentQuery, initRouter, navigateTo, registerRoute } from './router.js';

const appRoot = document.getElementById('app-root');
const mobileMenu = document.getElementById('mobile-menu');
const mobileToggle = document.getElementById('mobile-menu-toggle');
const loginLink = document.getElementById('login-link');
const registerLink = document.getElementById('register-link');
const logoutButton = document.getElementById('logout-button');

const PLACEHOLDER_IMAGE = 'https://images.unsplash.com/photo-1494526585095-c41746248156?auto=format&fit=crop&w=1200&q=80';

function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function formatPrice(value, currency = 'KGS') {
  if (value === null || value === undefined || value === '') return 'Price on request';

  const numericValue = Number(value);
  if (!Number.isFinite(numericValue)) return escapeHtml(String(value));

  if (currency === 'USD') {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(numericValue);
  }

  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'KGS', maximumFractionDigits: 0 }).format(numericValue);
}

function formatDate(value) {
  if (!value) return 'N/A';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString('en-GB', { year: 'numeric', month: 'short', day: 'numeric' });
}

function renderLoading(message = 'Loading...') {
  appRoot.innerHTML = `<div class="loading-state">${message}</div>`;
}

function renderError(message) {
  appRoot.innerHTML = `<div class="error-state"><h2>Something went wrong</h2><p>${escapeHtml(message)}</p></div>`;
}

function getCurrentQueryParams() {
  return getCurrentQuery();
}

function routeQueryParams() {
  return Object.fromEntries(getCurrentQueryParams().entries());
}

async function getCategories() {
  try {
    const result = await api.get('/api/categories');
    return Array.isArray(result?.data) ? result.data : [];
  } catch {
    return [];
  }
}

function getImageForProperty(property) {
  const images = Array.isArray(property?.images) ? property.images : [];
  const primaryImage = images.find((image) => image.is_primary) || images[0];
  return primaryImage?.image_url || PLACEHOLDER_IMAGE;
}

function getFavoriteState(propertyId, favoriteList = []) {
  return favoriteList.some((item) => Number(item.property_id) === Number(propertyId));
}

function bindFavoriteButtons() {
  document.querySelectorAll('[data-favorite-toggle]').forEach((button) => {
    button.onclick = async (event) => {
      event.preventDefault();
      event.stopPropagation();

      if (!authState.snapshot().isAuthenticated) {
        navigateTo('/login');
        return;
      }

      const propertyId = Number(button.dataset.propertyId);
      const isFavorite = button.dataset.favorite === 'true';

      try {
        if (isFavorite) {
          await api.delete(`/api/favorites/${propertyId}`);
        } else {
          await api.post('/api/favorites', { property_id: propertyId });
        }

        button.dataset.favorite = String(!isFavorite);
        button.textContent = !isFavorite ? '♥' : '♡';
        button.classList.toggle('is-active', !isFavorite);

        const currentHash = window.location.hash;
        if (currentHash === '#/favorites') {
          renderFavoritesPage();
        }
      } catch (error) {
        const message = error?.message || 'Unable to update favorite.';
        button.title = message;
      }
    };
  });
}

function renderPropertyCard(property, options = {}) {
  const favoriteState = options.favoriteState ?? false;
  const showFavoriteButton = options.showFavoriteButton !== false;
  const desiredTitle = property?.title || 'Property listing';
  const desiredPrice = formatPrice(property?.price, property?.currency || 'KGS');
  const propertyType = property?.property_type || 'property';
  const dealType = property?.deal_type || 'sale';
  const areaTotal = property?.area_total ? `${property.area_total} m²` : 'Area N/A';
  const rooms = property?.rooms ? `${property.rooms} rooms` : 'Rooms N/A';

  return `
    <article class="property-card">
      ${showFavoriteButton ? `<button type="button" class="favorite-toggle ${favoriteState ? 'is-active' : ''}" data-property-id="${property.id}" data-favorite="${favoriteState ? 'true' : 'false'}" aria-label="Toggle favorite">${favoriteState ? '♥' : '♡'}</button>` : ''}
      <img class="property-card__image" src="${getImageForProperty(property)}" alt="${escapeHtml(desiredTitle)}" loading="lazy" />
      <div class="property-card__body">
        <div class="property-card__meta">
          <span>${escapeHtml(propertyType)}</span>
          <span>${escapeHtml(dealType)}</span>
        </div>
        <h3>${escapeHtml(desiredTitle)}</h3>
        <div class="property-card__price">${desiredPrice}</div>
        <div class="property-card__details">
          <span>${property?.city_id ? `City #${property.city_id}` : 'Location N/A'}</span>
          <span>${escapeHtml(areaTotal)}</span>
          <span>${escapeHtml(rooms)}</span>
        </div>
        <div style="margin-top:1rem; display:flex; gap:.75rem; align-items:center;">
          <a class="btn btn-secondary" href="#/property/${property.id}">View details</a>
          ${showFavoriteButton ? '<button class="btn btn-ghost" type="button" data-property-id="'+property.id+'" data-favorite="'+ (favoriteState ? 'true' : 'false') +'" data-favorite-toggle>Save</button>' : ''}
        </div>
      </div>
    </article>
  `;
}

async function loadFeaturedProperties() {
  const container = document.getElementById('featured-properties');
  if (!container) return;

  try {
    const result = await api.get('/api/properties', { limit: 3, offset: 0 });
    const items = Array.isArray(result?.data) ? result.data : [];

    if (!items.length) {
      container.innerHTML = '<div class="empty-state">No active listings yet. Check back soon.</div>';
      return;
    }

    const favorites = authState.snapshot().isAuthenticated ? (await api.get('/api/favorites')).data || [] : [];
    container.innerHTML = items
      .map((property) => renderPropertyCard(property, { favoriteState: getFavoriteState(property.id, favorites) }))
      .join('');

    bindFavoriteButtons();
  } catch (error) {
    container.innerHTML = `<div class="error-state">${escapeHtml(error.message || 'Featured properties are unavailable.')}</div>`;
  }
}

async function renderHomePage() {
  appRoot.innerHTML = `
    <section class="page-section container">
      <div class="hero">
        <div class="hero-copy">
          <span class="status-badge">Premium marketplace</span>
          <h1>Find a home that fits your lifestyle.</h1>
          <p>Search verified listings, compare neighborhoods, and manage your favorites with the real DomKG backend.</p>
          <div class="hero-actions">
            <a href="#/search" class="btn btn-primary">Browse listings</a>
            <a href="#/create" class="btn btn-secondary">Sell property</a>
          </div>
        </div>
        <div class="hero-visual">
          <div class="search-panel">
            <h3>Search homes</h3>
            <form class="search-form" id="hero-search-form">
              <label>
                <span>Property type</span>
                <select name="property_type">
                  <option value="">Any type</option>
                  <option value="apartment">Apartment</option>
                  <option value="house">House</option>
                  <option value="land">Land</option>
                  <option value="commercial">Commercial</option>
                </select>
              </label>
              <label>
                <span>Deal type</span>
                <select name="deal_type">
                  <option value="">Any</option>
                  <option value="sale">Sale</option>
                  <option value="rent">Rent</option>
                </select>
              </label>
              <label>
                <span>Min price</span>
                <input type="number" min="0" name="min_price" placeholder="10000" />
              </label>
              <button type="submit" class="btn btn-primary">Search</button>
            </form>
          </div>
        </div>
      </div>
    </section>

    <section class="page-section container">
      <div class="section-header">
        <div>
          <p class="text-muted">Browse by category</p>
          <h2>Property categories</h2>
        </div>
      </div>
      <div class="grid-4" id="home-categories"></div>
    </section>

    <section class="page-section container">
      <div class="section-header">
        <div>
          <p class="text-muted">Fresh listings</p>
          <h2>Featured properties</h2>
        </div>
        <a href="#/search" class="btn btn-secondary">View all</a>
      </div>
      <div class="grid-3" id="featured-properties"></div>
    </section>

    <section class="page-section container">
      <div class="section-header">
        <div>
          <p class="text-muted">Why choose us</p>
          <h2>Built for easier property decisions</h2>
        </div>
      </div>
      <div class="grid-3">
        <article class="feature-card">
          <h3>Verified listings</h3>
          <p class="text-muted">A cleaner browsing experience with reliable property data from the backend.</p>
        </article>
        <article class="feature-card">
          <h3>Neighborhood-first</h3>
          <p class="text-muted">Browse listings by category, type, and budget without leaving the marketplace flow.</p>
        </article>
        <article class="feature-card">
          <h3>Simple ownership flow</h3>
          <p class="text-muted">Create, update, and save listings with a direct connection to the authenticated API.</p>
        </article>
      </div>
    </section>
  `;

  const homeSearchForm = document.getElementById('hero-search-form');
  homeSearchForm.addEventListener('submit', (event) => {
    event.preventDefault();
    const formData = new FormData(event.target);
    const params = new URLSearchParams();
    const propertyType = formData.get('property_type');
    const dealType = formData.get('deal_type');
    const minPrice = formData.get('min_price');

    if (propertyType) params.set('property_type', propertyType);
    if (dealType) params.set('deal_type', dealType);
    if (minPrice) params.set('min_price', minPrice);

    window.location.hash = `#/search${params.toString() ? `?${params.toString()}` : ''}`;
  });

  try {
    const categories = await getCategories();
    const categoriesContainer = document.getElementById('home-categories');
    if (categoriesContainer) {
      categoriesContainer.innerHTML = categories.length
        ? categories
            .map((category) => `
              <article class="category-card">
                <span class="tag">${escapeHtml(category.slug || 'Category')}</span>
                <h3>${escapeHtml(category.name)}</h3>
                <p class="text-muted">${escapeHtml(category.description || 'Browse listings in this category.')}</p>
              </article>
            `)
            .join('')
        : '<div class="empty-state">No categories are available right now.</div>';
    }
  } catch {
    document.getElementById('home-categories').innerHTML = '<div class="empty-state">Categories are temporarily unavailable.</div>';
  }

  await loadFeaturedProperties();
}

async function renderSearchPage() {
  const categories = await getCategories();
  const params = routeQueryParams();

  appRoot.innerHTML = `
    <section class="page-section container">
      <div class="page-header">
        <p class="text-muted">Browse</p>
        <h1>Search properties</h1>
      </div>
      <div class="form-shell">
        <form id="search-form" class="search-form">
          <label>
            <span>Category</span>
            <select name="category_id">
              <option value="">Any category</option>
              ${categories.map((category) => `<option value="${category.id}" ${params.category_id == category.id ? 'selected' : ''}>${escapeHtml(category.name)}</option>`).join('')}
            </select>
          </label>
          <label>
            <span>Property type</span>
            <select name="property_type">
              <option value="">Any type</option>
              <option value="apartment" ${params.property_type === 'apartment' ? 'selected' : ''}>Apartment</option>
              <option value="house" ${params.property_type === 'house' ? 'selected' : ''}>House</option>
              <option value="land" ${params.property_type === 'land' ? 'selected' : ''}>Land</option>
              <option value="commercial" ${params.property_type === 'commercial' ? 'selected' : ''}>Commercial</option>
            </select>
          </label>
          <label>
            <span>Deal type</span>
            <select name="deal_type">
              <option value="">Any</option>
              <option value="sale" ${params.deal_type === 'sale' ? 'selected' : ''}>Sale</option>
              <option value="rent" ${params.deal_type === 'rent' ? 'selected' : ''}>Rent</option>
            </select>
          </label>
          <label>
            <span>Min price</span>
            <input type="number" min="0" name="min_price" value="${escapeHtml(params.min_price || '')}" placeholder="50000" />
          </label>
          <label>
            <span>Max price</span>
            <input type="number" min="0" name="max_price" value="${escapeHtml(params.max_price || '')}" placeholder="300000" />
          </label>
          <label>
            <span>City ID</span>
            <input type="number" min="1" name="city_id" value="${escapeHtml(params.city_id || '')}" placeholder="1" />
          </label>
          <button type="submit" class="btn btn-primary">Apply filters</button>
        </form>
      </div>
      <div id="search-results" style="margin-top:2rem;"></div>
    </section>
  `;

  const searchForm = document.getElementById('search-form');
  searchForm.addEventListener('submit', (event) => {
    event.preventDefault();
    const formData = new FormData(event.target);
    const query = new URLSearchParams();

    for (const [key, value] of formData.entries()) {
      if (value !== '' && value !== null && value !== undefined) {
        query.set(key, String(value));
      }
    }

    window.location.hash = `#/search${query.toString() ? `?${query.toString()}` : ''}`;
  });

  const query = new URLSearchParams(window.location.hash.split('?')[1] || '');
  const resultTarget = document.getElementById('search-results');
  if (!resultTarget) return;

  const queryParams = {};
  for (const [key, value] of query.entries()) {
    queryParams[key] = value;
  }

  try {
    const result = await api.get('/api/properties', { limit: 12, offset: 0, ...queryParams });
    const items = Array.isArray(result?.data) ? result.data : [];

    if (!items.length) {
      resultTarget.innerHTML = '<div class="empty-state">No properties match the current filters.</div>';
      return;
    }

    const favorites = authState.snapshot().isAuthenticated ? (await api.get('/api/favorites')).data || [] : [];
    resultTarget.innerHTML = `
      <div class="section-header">
        <div>
          <p class="text-muted">Results</p>
          <h2>${items.length} property listings</h2>
        </div>
      </div>
      <div class="grid-3">
        ${items.map((property) => renderPropertyCard(property, { favoriteState: getFavoriteState(property.id, favorites) })).join('')}
      </div>
    `;

    bindFavoriteButtons();
  } catch (error) {
    resultTarget.innerHTML = `<div class="error-state">${escapeHtml(error.message || 'Unable to load listings.')}</div>`;
  }
}

async function loadPropertyDetail(propertyId) {
  const result = await api.get(`/api/properties/${propertyId}`);
  return result?.data || null;
}

async function renderPropertyDetailPage(path) {
  const match = path.match(/^\/property\/(\d+)$/);
  const propertyId = match ? Number(match[1]) : null;

  if (!propertyId) {
    appRoot.innerHTML = '<div class="error-state">Property id is missing.</div>';
    return;
  }

  renderLoading('Loading property details...');

  try {
    const property = await loadPropertyDetail(propertyId);
    if (!property) {
      appRoot.innerHTML = '<div class="error-state">Property not found.</div>';
      return;
    }

    const favorites = authState.snapshot().isAuthenticated ? (await api.get('/api/favorites')).data || [] : [];
    const isFavorite = getFavoriteState(propertyId, favorites);
    const primaryImage = getImageForProperty(property);
    const imageList = Array.isArray(property.images) && property.images.length ? property.images : [{ image_url: primaryImage, is_primary: true }];

    appRoot.innerHTML = `
      <section class="page-section container">
        <div class="page-header">
          <p class="text-muted">Property details</p>
          <h1>${escapeHtml(property.title || 'Property detail')}</h1>
        </div>
        <div class="grid-2">
          <div class="card" style="padding:var(--space-4)">
            <img src="${primaryImage}" alt="${escapeHtml(property.title || 'Property')}" style="width:100%;min-height:320px;object-fit:cover;border-radius:16px;" />
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(120px, 1fr)); gap:0.75rem; margin-top:1rem;">
              ${imageList.map((image) => `<img src="${image.image_url || PLACEHOLDER_IMAGE}" alt="${escapeHtml(property.title || 'Property')}" style="width:100%; height:110px; object-fit:cover; border-radius:12px;" loading="lazy" />`).join('')}
            </div>
          </div>
          <div class="card" style="padding:var(--space-6)">
            <div class="property-card__price">${formatPrice(property.price, property.currency || 'KGS')}</div>
            <div class="property-card__details" style="margin-bottom:1rem;">
              <span>${escapeHtml(property.property_type || 'Property')}</span>
              <span>${escapeHtml(property.deal_type || 'sale')}</span>
              <span>${escapeHtml(property.rooms ? `${property.rooms} rooms` : 'Rooms N/A')}</span>
            </div>
            <div style="display:flex; gap:.75rem; flex-wrap:wrap; margin-bottom:1rem;">
              <button type="button" class="btn btn-primary" data-favorite-toggle data-property-id="${property.id}" data-favorite="${isFavorite ? 'true' : 'false'}">${isFavorite ? 'Remove favorite' : 'Add favorite'}</button>
              ${authState.snapshot().currentUser && Number(authState.snapshot().currentUser.id) === Number(property.owner_id) ? `<a class="btn btn-secondary" href="#/property/${property.id}/edit">Edit property</a>` : ''}
            </div>
            <p class="text-muted">${escapeHtml(property.description || 'No description provided for this property.')}</p>
            <div class="grid-2" style="margin-top:1rem; gap:0.75rem;">
              <div><strong>Category</strong><p>${property.category_id ?? 'N/A'}</p></div>
              <div><strong>City</strong><p>${property.city_id ?? 'N/A'}</p></div>
              <div><strong>District</strong><p>${property.district_id ?? 'N/A'}</p></div>
              <div><strong>Area</strong><p>${property.area_total ? `${property.area_total} m²` : 'N/A'}</p></div>
              <div><strong>Address</strong><p>${escapeHtml(property.address || 'N/A')}</p></div>
              <div><strong>Published</strong><p>${formatDate(property.created_at)}</p></div>
            </div>
            ${property.owner ? `<div style="margin-top:1rem;"><h3>Owner</h3><p>${escapeHtml(property.owner.first_name || 'Owner')} ${escapeHtml(property.owner.last_name || '')}</p><p>${escapeHtml(property.owner.phone || 'Phone not shared')}</p></div>` : ''}
          </div>
        </div>
      </section>
    `;

    bindFavoriteButtons();
  } catch (error) {
    renderError(error.message || 'Unable to load the property details.');
  }
}

async function renderFavoritesPage() {
  const state = authState.snapshot();
  if (!state.isAuthenticated) {
    appRoot.innerHTML = '<div class="error-state">Please log in to view favorites.</div>';
    return;
  }

  renderLoading('Loading your favorites...');

  try {
    const result = await api.get('/api/favorites');
    const favorites = Array.isArray(result?.data) ? result.data : [];

    if (!favorites.length) {
      appRoot.innerHTML = '<div class="empty-state">No favorites yet. Save a property to see it here.</div>';
      return;
    }

    const propertyRequests = favorites.map(async (favorite) => {
      try {
        const propertyResult = await api.get(`/api/properties/${favorite.property_id}`);
        return propertyResult?.data || null;
      } catch {
        return null;
      }
    });

    const properties = (await Promise.all(propertyRequests)).filter(Boolean);

    if (!properties.length) {
      appRoot.innerHTML = '<div class="empty-state">No favorite properties were available to display.</div>';
      return;
    }

    appRoot.innerHTML = `
      <section class="page-section container">
        <div class="page-header">
          <p class="text-muted">Saved homes</p>
          <h1>Your favorites</h1>
        </div>
        <div class="grid-3">
          ${properties.map((property) => renderPropertyCard(property, { favoriteState: true })).join('')}
        </div>
      </section>
    `;

    bindFavoriteButtons();
  } catch (error) {
    renderError(error.message || 'Unable to load favorites.');
  }
}

async function renderProfilePage() {
  const state = authState.snapshot();
  if (!state.isAuthenticated) {
    appRoot.innerHTML = '<div class="error-state">You need to log in to view your profile.</div>';
    return;
  }

  renderLoading('Loading your profile...');

  try {
    const result = await api.get('/api/auth/me');
    const user = result?.data || {};

    appRoot.innerHTML = `
      <section class="page-section container">
        <div class="page-header">
          <p class="text-muted">Account</p>
          <h1>Profile</h1>
        </div>
        <div class="form-shell">
          <h2>${escapeHtml(user.first_name || 'User')}</h2>
          <p><strong>Email:</strong> ${escapeHtml(user.email || 'N/A')}</p>
          <p><strong>Phone:</strong> ${escapeHtml(user.phone || 'N/A')}</p>
          <p><strong>Role:</strong> ${escapeHtml(user.role || 'user')}</p>
          <p><strong>Verified:</strong> ${user.is_verified ? 'Yes' : 'No'}</p>
          <p><strong>Joined:</strong> ${formatDate(user.created_at)}</p>
        </div>
      </section>
    `;
  } catch (error) {
    renderError(error.message || 'Unable to load profile.');
  }
}

function renderLoginPage() {
  appRoot.innerHTML = `
    <section class="page-section container auth-layout">
      <div class="form-shell">
        <h1>Welcome back</h1>
        <form id="login-form" class="form-grid">
          <label style="grid-column:1 / -1">
            <span>Email</span>
            <input name="email" type="email" placeholder="you@example.com" required />
          </label>
          <label style="grid-column:1 / -1">
            <span>Password</span>
            <input name="password" type="password" placeholder="Password" required />
          </label>
          <button class="btn btn-primary" type="submit">Log in</button>
        </form>
      </div>
      <div class="info-card">
        <h2>Need an account?</h2>
        <p class="text-muted">Create a profile and access your saved homes and created listings.</p>
        <a href="#/register" class="btn btn-secondary">Register</a>
      </div>
    </section>
  `;

  document.getElementById('login-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const formData = new FormData(event.target);

    try {
      const result = await api.post('/api/auth/login', {
        email: formData.get('email'),
        password: formData.get('password'),
      });

      const payload = result?.data || {};
      authState.setSession({
        user: payload.user,
        accessToken: payload.access_token,
        refreshToken: payload.refresh_token,
      });
      navigateTo('/');
    } catch (error) {
      renderError(error.message || 'Login failed.');
    }
  });
}

function renderRegisterPage() {
  appRoot.innerHTML = `
    <section class="page-section container auth-layout">
      <div class="form-shell">
        <h1>Create account</h1>
        <form id="register-form" class="form-grid">
          <label>
            <span>First name</span>
            <input name="first_name" type="text" placeholder="Aigerim" required />
          </label>
          <label>
            <span>Last name</span>
            <input name="last_name" type="text" placeholder="Toktonalieva" />
          </label>
          <label style="grid-column:1 / -1">
            <span>Email</span>
            <input name="email" type="email" placeholder="you@example.com" required />
          </label>
          <label style="grid-column:1 / -1">
            <span>Password</span>
            <input name="password" type="password" placeholder="Minimum 6 characters" required />
          </label>
          <button class="btn btn-primary" type="submit">Create account</button>
        </form>
      </div>
      <div class="info-card">
        <h2>Already have an account?</h2>
        <p class="text-muted">Use your current credentials to continue managing listings and favorites.</p>
        <a href="#/login" class="btn btn-secondary">Log in</a>
      </div>
    </section>
  `;

  document.getElementById('register-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const formData = new FormData(event.target);

    try {
      const result = await api.post('/api/auth/register', {
        email: formData.get('email'),
        password: formData.get('password'),
        first_name: formData.get('first_name'),
        last_name: formData.get('last_name'),
      });

      const payload = result?.data || {};
      authState.setSession({
        user: payload.user,
        accessToken: payload.access_token,
        refreshToken: payload.refresh_token,
      });
      navigateTo('/');
    } catch (error) {
      renderError(error.message || 'Registration failed.');
    }
  });
}

function renderNotFound() {
  appRoot.innerHTML = '<div class="error-state"><h1>404</h1><p>Page not found.</p></div>';
}

async function renderCreatePage() {
  if (!authState.snapshot().isAuthenticated) {
    navigateTo('/login');
    return;
  }

  const categories = await getCategories();

  appRoot.innerHTML = `
    <section class="page-section container">
      <div class="page-header">
        <p class="text-muted">Create listing</p>
        <h1>Publish your property</h1>
      </div>
      <div class="form-shell">
        <form id="create-property-form" class="form-grid">
          <label>
            <span>Title</span>
            <input name="title" type="text" placeholder="2-bedroom apartment" required />
          </label>
          <label>
            <span>Price</span>
            <input name="price" type="number" min="0" step="0.01" placeholder="95000" required />
          </label>
          <label>
            <span>Category</span>
            <select name="category_id" required>
              <option value="">Select category</option>
              ${categories.map((category) => `<option value="${category.id}">${escapeHtml(category.name)}</option>`).join('')}
            </select>
          </label>
          <label>
            <span>City ID</span>
            <input name="city_id" type="number" min="1" value="1" required />
          </label>
          <label>
            <span>District ID</span>
            <input name="district_id" type="number" min="1" placeholder="Optional" />
          </label>
          <label>
            <span>Property type</span>
            <select name="property_type">
              <option value="apartment">Apartment</option>
              <option value="house">House</option>
              <option value="land">Land</option>
              <option value="commercial">Commercial</option>
            </select>
          </label>
          <label>
            <span>Deal type</span>
            <select name="deal_type">
              <option value="sale">Sale</option>
              <option value="rent">Rent</option>
            </select>
          </label>
          <label>
            <span>Rooms</span>
            <input name="rooms" type="number" min="1" placeholder="3" />
          </label>
          <label>
            <span>Area total (m²)</span>
            <input name="area_total" type="number" min="0" step="0.01" placeholder="90" />
          </label>
          <label style="grid-column:1 / -1">
            <span>Address</span>
            <input name="address" type="text" placeholder="Main street, Bishkek" />
          </label>
          <label style="grid-column:1 / -1">
            <span>Description</span>
            <textarea name="description" placeholder="Describe the property and what makes it unique."></textarea>
          </label>
          <button class="btn btn-primary" type="submit">Create property</button>
        </form>
      </div>
    </section>
  `;

  const form = document.getElementById('create-property-form');
  form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const formData = new FormData(form);
    const payload = {
      title: String(formData.get('title') || '').trim(),
      description: String(formData.get('description') || '').trim() || null,
      price: Number(formData.get('price')),
      category_id: Number(formData.get('category_id')),
      city_id: Number(formData.get('city_id')),
      district_id: formData.get('district_id') ? Number(formData.get('district_id')) : null,
      property_type: formData.get('property_type') || 'apartment',
      deal_type: formData.get('deal_type') || 'sale',
      rooms: formData.get('rooms') ? Number(formData.get('rooms')) : null,
      area_total: formData.get('area_total') ? Number(formData.get('area_total')) : null,
      address: String(formData.get('address') || '').trim() || null,
    };

    try {
      const result = await api.post('/api/properties', payload);
      const propertyId = result?.data?.id;
      if (propertyId) {
        navigateTo(`/property/${propertyId}`);
      }
    } catch (error) {
      renderError(error.message || 'Unable to create the property.');
    }
  });
}

async function renderEditPropertyPage(path) {
  const match = path.match(/^\/property\/(\d+)\/edit$/);
  const propertyId = match ? Number(match[1]) : null;

  if (!propertyId) {
    appRoot.innerHTML = '<div class="error-state">Property id is missing.</div>';
    return;
  }

  if (!authState.snapshot().isAuthenticated) {
    navigateTo('/login');
    return;
  }

  try {
    const property = await loadPropertyDetail(propertyId);
    const categories = await getCategories();
    const currentUser = authState.snapshot().currentUser;

    if (!property) {
      appRoot.innerHTML = '<div class="error-state">Property not found.</div>';
      return;
    }

    if (Number(currentUser?.id) !== Number(property.owner_id) && currentUser?.role !== 'admin') {
      appRoot.innerHTML = '<div class="error-state">You are not allowed to edit this property.</div>';
      return;
    }

    appRoot.innerHTML = `
      <section class="page-section container">
        <div class="page-header">
          <p class="text-muted">Edit listing</p>
          <h1>Update property</h1>
        </div>
        <div class="form-shell">
          <form id="edit-property-form" class="form-grid">
            <label>
              <span>Title</span>
              <input name="title" type="text" value="${escapeHtml(property.title || '')}" required />
            </label>
            <label>
              <span>Price</span>
              <input name="price" type="number" min="0" step="0.01" value="${escapeHtml(property.price || '')}" required />
            </label>
            <label>
              <span>Category</span>
              <select name="category_id" required>
                ${categories.map((category) => `<option value="${category.id}" ${Number(property.category_id) === Number(category.id) ? 'selected' : ''}>${escapeHtml(category.name)}</option>`).join('')}
              </select>
            </label>
            <label>
              <span>City ID</span>
              <input name="city_id" type="number" min="1" value="${escapeHtml(property.city_id || 1)}" required />
            </label>
            <label>
              <span>District ID</span>
              <input name="district_id" type="number" min="1" value="${escapeHtml(property.district_id || '')}" placeholder="Optional" />
            </label>
            <label>
              <span>Property type</span>
              <select name="property_type">
                <option value="apartment" ${property.property_type === 'apartment' ? 'selected' : ''}>Apartment</option>
                <option value="house" ${property.property_type === 'house' ? 'selected' : ''}>House</option>
                <option value="land" ${property.property_type === 'land' ? 'selected' : ''}>Land</option>
                <option value="commercial" ${property.property_type === 'commercial' ? 'selected' : ''}>Commercial</option>
              </select>
            </label>
            <label>
              <span>Deal type</span>
              <select name="deal_type">
                <option value="sale" ${property.deal_type === 'sale' ? 'selected' : ''}>Sale</option>
                <option value="rent" ${property.deal_type === 'rent' ? 'selected' : ''}>Rent</option>
              </select>
            </label>
            <label>
              <span>Rooms</span>
              <input name="rooms" type="number" min="1" value="${escapeHtml(property.rooms || '')}" />
            </label>
            <label>
              <span>Area total (m²)</span>
              <input name="area_total" type="number" min="0" step="0.01" value="${escapeHtml(property.area_total || '')}" />
            </label>
            <label style="grid-column:1 / -1">
              <span>Address</span>
              <input name="address" type="text" value="${escapeHtml(property.address || '')}" />
            </label>
            <label style="grid-column:1 / -1">
              <span>Description</span>
              <textarea name="description">${escapeHtml(property.description || '')}</textarea>
            </label>
            <button class="btn btn-primary" type="submit">Save changes</button>
          </form>
        </div>
      </section>
    `;

    const form = document.getElementById('edit-property-form');
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const formData = new FormData(form);
      const payload = {
        title: String(formData.get('title') || '').trim(),
        description: String(formData.get('description') || '').trim() || null,
        price: Number(formData.get('price')),
        category_id: Number(formData.get('category_id')),
        city_id: Number(formData.get('city_id')),
        district_id: formData.get('district_id') ? Number(formData.get('district_id')) : null,
        property_type: formData.get('property_type') || 'apartment',
        deal_type: formData.get('deal_type') || 'sale',
        rooms: formData.get('rooms') ? Number(formData.get('rooms')) : null,
        area_total: formData.get('area_total') ? Number(formData.get('area_total')) : null,
        address: String(formData.get('address') || '').trim() || null,
      };

      try {
        await api.patch(`/api/properties/${propertyId}`, payload);
        navigateTo(`/property/${propertyId}`);
      } catch (error) {
        renderError(error.message || 'Unable to update the property.');
      }
    });
  } catch (error) {
    renderError(error.message || 'Unable to load the property for editing.');
  }
}

async function renderAdminPage() {
  const state = authState.snapshot();
  if (!state.isAuthenticated || state.currentUser?.role !== 'admin') {
    appRoot.innerHTML = '<div class="error-state">Admin access is required.</div>';
    return;
  }

  renderLoading('Loading admin dashboard...');

  try {
    const [statsResult, reportsResult] = await Promise.all([
      api.get('/api/admin/stats'),
      api.get('/api/admin/reports'),
    ]);

    const stats = statsResult?.data || {};
    const reports = Array.isArray(reportsResult?.data) ? reportsResult.data : [];

    appRoot.innerHTML = `
      <section class="page-section container">
        <div class="page-header">
          <p class="text-muted">Admin panel</p>
          <h1>Marketplace overview</h1>
        </div>
        <div class="grid-3">
          <div class="card" style="padding:var(--space-5)"><h3>Total users</h3><p>${stats.total_users ?? 0}</p></div>
          <div class="card" style="padding:var(--space-5)"><h3>Total properties</h3><p>${stats.total_properties ?? 0}</p></div>
          <div class="card" style="padding:var(--space-5)"><h3>Pending reports</h3><p>${stats.pending_reports ?? 0}</p></div>
        </div>
        <div style="margin-top:2rem;">
          <h2>Reports</h2>
          ${reports.length ? `<div class="grid-3">${reports.map((report) => `
            <article class="card" style="padding:var(--space-5)">
              <h3>Report #${report.id}</h3>
              <p><strong>Property:</strong> ${report.property_id}</p>
              <p><strong>Status:</strong> ${escapeHtml(report.status || 'pending')}</p>
              <p>${escapeHtml(report.reason || 'No reason provided')}</p>
            </article>
          `).join('')}</div>` : '<div class="empty-state">No reports are currently pending.</div>'}
        </div>
      </section>
    `;
  } catch (error) {
    renderError(error.message || 'Unable to load the admin dashboard.');
  }
}

function renderNavigation() {
  const state = authState.snapshot();
  const nav = document.querySelector('.main-nav');
  if (!nav) return;

  if (state.isAuthenticated) {
    nav.innerHTML = `
      <a href="#/">Home</a>
      <a href="#/search">Search</a>
      <a href="#/create">Add property</a>
      <a href="#/favorites">Favorites</a>
      <a href="#/profile">Profile</a>
      ${state.currentUser?.role === 'admin' ? '<a href="#/admin">Admin</a>' : ''}
    `;
  } else {
    nav.innerHTML = `
      <a href="#/">Home</a>
      <a href="#/search">Search</a>
    `;
  }

  const mobileNav = document.getElementById('mobile-menu');
  if (mobileNav) {
    mobileNav.innerHTML = state.isAuthenticated
      ? `
        <a href="#/">Home</a>
        <a href="#/search">Search</a>
        <a href="#/create">Add property</a>
        <a href="#/favorites">Favorites</a>
        <a href="#/profile">Profile</a>
        ${state.currentUser?.role === 'admin' ? '<a href="#/admin">Admin</a>' : ''}
        <a href="#/login">Log in</a>
      `
      : `
        <a href="#/">Home</a>
        <a href="#/search">Search</a>
        <a href="#/login">Log in</a>
        <a href="#/register">Register</a>
      `;
  }
}

function updateAuthUI() {
  const state = authState.snapshot();
  const visible = state.isAuthenticated;

  if (loginLink) loginLink.classList.toggle('hidden', visible);
  if (registerLink) registerLink.classList.toggle('hidden', visible);
  if (logoutButton) logoutButton.classList.toggle('hidden', !visible);

  renderNavigation();
}

function bindGlobalEvents() {
  if (mobileToggle && mobileMenu) {
    mobileToggle.addEventListener('click', () => {
      mobileMenu.classList.toggle('hidden');
    });
  }

  if (logoutButton) {
    logoutButton.addEventListener('click', async () => {
      try {
        await api.logout();
      } catch {
        // ignore logout errors and continue clearing local state.
      }
      authState.clearSession();
      navigateTo('/');
    });
  }
}

function initApp() {
  bindGlobalEvents();
  registerRoute('/', renderHomePage);
  registerRoute('/search', renderSearchPage);
  registerRoute('/property/:id', renderPropertyDetailPage);
  registerRoute('/property/:id/edit', renderEditPropertyPage);
  registerRoute('/create', renderCreatePage);
  registerRoute('/favorites', renderFavoritesPage);
  registerRoute('/profile', renderProfilePage);
  registerRoute('/login', renderLoginPage);
  registerRoute('/register', renderRegisterPage);
  registerRoute('/admin', renderAdminPage);
  registerRoute('/not-found', renderNotFound);

  authState.subscribe(() => updateAuthUI());
  updateAuthUI();
  initRouter();
}

initApp();
