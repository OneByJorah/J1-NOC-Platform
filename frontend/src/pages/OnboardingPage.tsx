import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { get, post } from '../services/api';

export default function OnboardingPage() {
  const navigate = useNavigate();
  const [needsSetup, setNeedsSetup] = useState<boolean | null>(null);
  const [form, setForm] = useState({ username: '', email: '', password: '', passwordConfirm: '', full_name: '' });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    get('/setup/status')
      .then((res: any) => setNeedsSetup(Boolean(res?.needs_setup)))
      .catch(() => setNeedsSetup(false));
  }, []);

  if (needsSetup === null) {
    return (
      <div className="auth-page">
        <div className="auth-card">
          <p className="dim">Checking setup status…</p>
        </div>
      </div>
    );
  }

  if (!needsSetup) {
    return (
      <div className="auth-page">
        <div className="auth-card">
          <h2>Setup complete</h2>
          <p className="dim">An admin account already exists. Please sign in.</p>
          <button onClick={() => navigate('/login')} style={{ marginTop: 12 }}>Go to login</button>
        </div>
      </div>
    );
  }

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (form.password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }
    if (form.password !== form.passwordConfirm) {
      setError('Passwords do not match');
      return;
    }
    setLoading(true);
    try {
      await post('/setup', {
        username: form.username,
        email: form.email || undefined,
        password: form.password,
        full_name: form.full_name || undefined,
      });
      navigate('/login');
    } catch (err: any) {
      setError(err?.message || 'Setup failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <form className="auth-card" onSubmit={submit}>
        <h2>Welcome to J1 NOC</h2>
        <p className="dim">Create the first administrator account.</p>
        {error && <div className="error">{error}</div>}
        <label>
          <span>Username</span>
          <input value={form.username} onChange={e => setForm({ ...form, username: e.target.value })} required />
        </label>
        <label>
          <span>Full name</span>
          <input value={form.full_name} onChange={e => setForm({ ...form, full_name: e.target.value })} />
        </label>
        <label>
          <span>Email</span>
          <input type="email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} />
        </label>
        <label>
          <span>Password</span>
          <input type="password" value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} required />
        </label>
        <label>
          <span>Confirm password</span>
          <input type="password" value={form.passwordConfirm} onChange={e => setForm({ ...form, passwordConfirm: e.target.value })} required />
        </label>
        <button disabled={loading}>{loading ? 'Creating…' : 'Create admin'}</button>
      </form>
    </div>
  );
}
