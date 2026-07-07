// Normalize base so it ALWAYS ends with a single slash. Without this, a
// `VITE_API_URL=/api` build emits `/apisystem/overview` (no separator) which
// nginx routes to the SPA and the dashboard hangs on "Loading…".
const rawBase = import.meta.env.VITE_API_URL ?? '/api/';
const base = rawBase.endsWith('/') ? rawBase : `${rawBase}/`;
const statusHTTP204 = 204;

async function request(url: string, init: RequestInit = {}) {
  const token = localStorage.getItem('token');
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  if (token) headers.Authorization = `Bearer ${token}`;
  const body = init.body ? JSON.stringify(init.body) : undefined;
  const res = await fetch(`${base}${url.replace(/^\//, '')}`, {
    ...init,
    headers: { ...headers, ...(init.headers || {}) },
    body,
  });

  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(text || `Request failed (${res.status})`);
  }
  if (res.status === statusHTTP204 || res.headers.get('content-length') === '0') return null;
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

export async function patch(url: string, body: unknown) {
  return request(url, { method: 'PATCH', body: JSON.stringify(body) });
}

export async function del(url: string) {
  return request(url, { method: 'DELETE' });
}

export async function postForm(url: string, form: FormData) {
  const token = localStorage.getItem('token');
  const headers: Record<string, string> = {};
  if (token) headers.Authorization = `Bearer ${token}`;
  const res = await fetch(`${base}${url.replace(/^\//, '')}`, {
    method: 'POST',
    headers,
    body: form as any,
  });
  if (!res.ok) throw new Error('Request failed');
  return res.json().catch(() => null);
}
