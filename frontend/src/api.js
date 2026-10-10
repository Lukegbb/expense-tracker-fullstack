const ACCESS_KEY = 'et_access';
const REFRESH_KEY = 'et_refresh';

export const isLoggedIn = () => Boolean(localStorage.getItem(ACCESS_KEY));

export function logout() {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

async function refreshAccessToken() {
  const refresh = localStorage.getItem(REFRESH_KEY);
  if (!refresh) return false;
  const res = await fetch('/api/auth/token/refresh/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh }),
  });
  if (!res.ok) return false;
  const data = await res.json();
  localStorage.setItem(ACCESS_KEY, data.access);
  return true;
}

async function request(path, { method = 'GET', body, retry = true } = {}) {
  const headers = { 'Content-Type': 'application/json' };
  const token = localStorage.getItem(ACCESS_KEY);
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`/api${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  // Access token expired: try once with a refreshed token.
  if (res.status === 401 && retry && (await refreshAccessToken())) {
    return request(path, { method, body, retry: false });
  }
  if (res.status === 204) return null;

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const message =
      data.detail ||
      Object.entries(data)
        .map(([field, errors]) => `${field}: ${[].concat(errors).join(' ')}`)
        .join(' | ') ||
      `Request failed (${res.status})`;
    throw new Error(message);
  }
  return data;
}

const toQuery = (params) => {
  const query = new URLSearchParams(
    Object.entries(params).filter(([, value]) => value !== '' && value != null)
  ).toString();
  return query ? `?${query}` : '';
};

export const api = {
  async login(username, password) {
    const data = await request('/auth/token/', {
      method: 'POST',
      body: { username, password },
      retry: false,
    });
    localStorage.setItem(ACCESS_KEY, data.access);
    localStorage.setItem(REFRESH_KEY, data.refresh);
  },
  register: (payload) => request('/auth/register/', { method: 'POST', body: payload, retry: false }),
  categories: () => request('/categories/'),
  transactions: (params = {}) => request(`/transactions/${toQuery(params)}`),
  createTransaction: (payload) => request('/transactions/', { method: 'POST', body: payload }),
  deleteTransaction: (id) => request(`/transactions/${id}/`, { method: 'DELETE' }),
  summary: (month) => request(`/reports/summary/${toQuery({ month })}`),
  monthly: (months = 6) => request(`/reports/monthly/${toQuery({ months })}`),
};
