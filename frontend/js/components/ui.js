function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

export function safeText(value) {
  return escapeHtml(value);
}

export function ensureUiRoot() {
  let root = document.getElementById('domkg-ui-root');
  if (!root) {
    root = document.createElement('div');
    root.id = 'domkg-ui-root';
    root.setAttribute('aria-live', 'polite');
    document.body.appendChild(root);
  }
  return root;
}

export const ui = {
  loading(message = 'Loading...') {
    return `<div class="loading-state" role="status" aria-live="polite">${safeText(message)}</div>`;
  },

  empty(title, description = '') {
    return `
      <div class="empty-state" role="status">
        <h3>${safeText(title)}</h3>
        ${description ? `<p>${safeText(description)}</p>` : ''}
      </div>
    `;
  },

  error(title = 'Something went wrong', message = '') {
    return `
      <div class="error-state" role="alert">
        <h3>${safeText(title)}</h3>
        ${message ? `<p>${safeText(message)}</p>` : ''}
      </div>
    `;
  },

  toast(message, type = 'success') {
    const root = ensureUiRoot();
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.setAttribute('role', 'status');
    toast.textContent = message;
    root.appendChild(toast);

    window.setTimeout(() => {
      toast.classList.add('is-visible');
    }, 10);

    window.setTimeout(() => {
      toast.classList.add('is-closing');
      window.setTimeout(() => toast.remove(), 220);
    }, 2600);
  },

  confirm(message, onConfirm, onCancel = null) {
    const root = ensureUiRoot();
    const overlay = document.createElement('div');
    overlay.className = 'modal-backdrop';
    overlay.innerHTML = `
      <div class="modal-dialog" role="dialog" aria-modal="true" aria-labelledby="confirm-title">
        <div class="modal-header">
          <h3 id="confirm-title">Confirm action</h3>
          <button type="button" class="modal-close" aria-label="Close dialog">×</button>
        </div>
        <div class="modal-body">
          <p>${safeText(message)}</p>
        </div>
        <div class="modal-actions">
          <button type="button" class="btn btn-ghost cancel-action">Cancel</button>
          <button type="button" class="btn btn-primary confirm-action">Confirm</button>
        </div>
      </div>
    `;
    root.appendChild(overlay);

    const close = () => overlay.remove();
    overlay.querySelector('.modal-close').onclick = close;
    overlay.querySelector('.cancel-action').onclick = () => {
      if (onCancel) onCancel();
      close();
    };
    overlay.querySelector('.confirm-action').onclick = () => {
      onConfirm();
      close();
    };
  },

  modal({ title, content, actions = [] }) {
    const root = ensureUiRoot();
    const overlay = document.createElement('div');
    overlay.className = 'modal-backdrop';
    overlay.innerHTML = `
      <div class="modal-dialog" role="dialog" aria-modal="true" aria-labelledby="modal-title">
        <div class="modal-header">
          <h3 id="modal-title">${safeText(title)}</h3>
          <button type="button" class="modal-close" aria-label="Close dialog">×</button>
        </div>
        <div class="modal-body">${content}</div>
        <div class="modal-actions">${actions.map((action) => `<button type="button" class="${action.className || 'btn btn-secondary'}" data-action="${safeText(action.name)}">${safeText(action.label)}</button>`).join('')}</div>
      </div>
    `;
    root.appendChild(overlay);

    const close = () => overlay.remove();
    overlay.querySelector('.modal-close').onclick = close;
    overlay.querySelectorAll('[data-action]').forEach((button) => {
      button.onclick = () => {
        const action = actions.find((entry) => entry.name === button.dataset.action);
        if (action && action.onClick) action.onClick();
      };
    });
    return overlay;
  },

  skeletonGrid(count = 3) {
    return Array.from({ length: count }, () => `
      <div class="skeleton-card">
        <div class="skeleton skeleton-image"></div>
        <div class="skeleton skeleton-line short"></div>
        <div class="skeleton skeleton-line"></div>
        <div class="skeleton skeleton-line medium"></div>
      </div>
    `).join('');
  },
};
