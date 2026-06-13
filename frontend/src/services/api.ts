const base = import.meta.env.VITE_API_URL || '/api';

export async function get(url: string) {
  const res = await fetch(`${base}${url}`);
  if (!res.ok) throw new Error('Request failed');
  return res.json();
}

export async function post(url: string, body: unknown) {
  const res = await fetch(`${base}${url}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error('Request failed');
  return res.json();
}
