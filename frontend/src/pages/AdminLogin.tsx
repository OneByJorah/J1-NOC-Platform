import { useEffect, useState } from 'react';
import { login as adminLogin } from '../services/adminApi';

type LoginResponse = { ok?: boolean; token?: string; user?: { username?: string; role?: string } };

type LoginState = {
  token: string;
  user: {
    username: string;
    role?: string;
  };
};

const fallbackUser = { username: 'guest', role: 'admin' as const };

export default function AdminLogin({ onLogin }: { onLogin: (payload: LoginState) => void }) {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const data = (await adminLogin(username, password)) as LoginResponse;
      if (!data?.ok || !data.token) throw new Error('Invalid credentials');
      localStorage.setItem('admin_token', data.token);
      if (data.user) localStorage.setItem('admin_user', JSON.stringify(data.user));
      onLogin({
        token: data.token,
        user: {
          username: data.user?.username || username,
          role: data.user?.role || 'admin',
        },
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-wrap">
      <form className="login-card" onSubmit={submit}>
        <h2>Admin Login</h2>
        <label>
          <span>Username</span>
          <input value={username} onChange={(e) => setUsername(e.target.value)} />
        </label>
        <label>
          <span>Password</span>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </label>
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={loading}>{loading ? 'Signing in…' : 'Sign in'}</button>
      </form>
    </div>
  );
}
