const ADMIN_BASE = '/admin/api/admin';

async function request(url: string, init: RequestInit = {}) {
  const token = localStorage.getItem('admin_token');
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const body = init.body ? JSON.stringify(init.body) : undefined;
  const res = await fetch(`${ADMIN_BASE}${url}`, {
    ...init,
    headers: { ...headers, ...(init.headers || {}) },
    body,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(text || `Request failed (${res.status})`);
  }
  if ([204].includes(res.status) || res.headers.get('content-length') === '0') return null;
  return res.json().catch(() => null);
}

export async function get(url: string) {
  return request(url);
}

export async function post(url: string, body: unknown) {
  return request(url, { method: 'POST', body: JSON.stringify(body) });
}

export async function put(url: string, body: unknown) {
  return request(url, { method: 'PUT', body: JSON.stringify(body) });
}

export async function del(url: string) {
  return request(url, { method: 'DELETE' });
}

export async function login(username: string, password: string) {
  return request('/auth/login', { method: 'POST', body: JSON.stringify({ username, password }) });
}
