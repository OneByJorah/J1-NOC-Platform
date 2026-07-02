import { useEffect, useState, useMemo } from 'react';
import { Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { get, post, del } from '../services/api';
import AdminLogin from './AdminLogin';

type Tab = {
  id: number;
  path: string;
  label: string;
  sort_order: number;
  is_visible: boolean;
  icon?: string | null;
  created_at: string;
  updated_at: string;
};

type Role = {
  id: number;
  name: string;
  slug: string;
  description?: string | null;
  permissions?: Record<string, unknown>;
};

type AdminUser = {
  id: number;
  username: string;
  email?: string | null;
  full_name?: string | null;
  role?: Role | string;
  is_active: boolean;
  is_locked: boolean;
};

export default function AdminPanel() {
  const navigate = useNavigate();
  const [authed, setAuthed] = useState<boolean>(() => Boolean(localStorage.getItem('admin_token')));
  const [showLogin, setShowLogin] = useState<boolean>(() => !Boolean(localStorage.getItem('admin_token')));

  const handleLogin = () => setAuthed(true);
  const handleLogout = () => {
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_user');
    setAuthed(false);
    setShowLogin(true);
    navigate('/');
  };

  if (!authed || showLogin) {
    return <AdminLogin onLogin={handleLogin} />;
  }

  const location = useLocation();
  const [tabs, setTabs] = useState<Tab[]>([]);

  useEffect(() => {
    let cancelled = false;
    get('/admin/tabs')
      .then((res) => {
        if (!cancelled && res && typeof res === 'object') setTabs((res as { tabs?: Tab[] }).tabs || []);
      })
      .catch(() => {
        if (!cancelled) setTabs([]);
      });
    return () => { cancelled = true; };
  }, []);

  const subnav = useMemo(
    () => [
      { key: 'tabs', to: '/admin/tabs', label: 'Tabs' },
      { key: 'users', to: '/admin/users', label: 'Users' },
      { key: 'roles', to: '/admin/roles', label: 'Roles' },
    ],
    [],
  );

  const raw = location.pathname.replace(/^\/admin\/?/, '') || 'tabs';
  const active = (['tabs', 'users', 'roles'] as const).includes(raw as 'tabs' | 'users' | 'roles') ? (raw as 'tabs' | 'users' | 'roles') : 'tabs';

  return (
    <div className="admin-shell">
      <header className="admin-header">
        <h1>Admin Console</h1>
        <span className="admin-badge">admin</span>
        <button onClick={handleLogout}>Logout</button>
      </header>
      <nav className="admin-subnav">
        {subnav.map((item) => (
          <button
            key={item.key}
            className={`admin-subnav-btn ${active === item.key ? 'active' : ''}`}
            onClick={() => navigate(item.to)}
          >
            {item.label}
          </button>
        ))}
      </nav>
      <div className="admin-body">
        <Routes>
          <Route path="/" element={<TabsManager tabs={tabs} onChange={setTabs} />} />
          <Route path="tabs" element={<TabsManager tabs={tabs} onChange={setTabs} />} />
          <Route path="users" element={<UsersManager />} />
          <Route path="roles" element={<RolesManager />} />
          <Route path="*" element={<Navigate to="/admin/tabs" replace />} />
        </Routes>
      </div>
    </div>
  );
}

function TabsManager({ tabs, onChange }: { tabs: Tab[]; onChange: (t: Tab[]) => void }) {
  const [form, setForm] = useState({ path: '', label: '', sort_order: 1, is_visible: true, icon: '' });

  const submit = async () => {
    if (!form.path || !form.label) return;
    const body = {
      path: form.path,
      label: form.label,
      sort_order: Number(form.sort_order) || 0,
      is_visible: Boolean(form.is_visible),
      icon: form.icon || null,
    };
    const res = (await post('/admin/tabs', body)) as Tab;
    onChange([...(tabs || []), res]);
    setForm({ path: '', label: '', sort_order: 1, is_visible: true, icon: '' });
  };

  const remove = async (id: number) => {
    await del(`/admin/tabs/${id}`);
    onChange((tabs || []).filter((t) => t.id !== id));
  };

  return (
    <div className="admin-section">
      <div className="admin-card">
        <h3>Add tab</h3>
        <div className="admin-form">
          <label>
            Path
            <input value={form.path} onChange={(e) => setForm({ ...form, path: e.target.value })} placeholder="/my-tab" />
          </label>
          <label>
            Label
            <input value={form.label} onChange={(e) => setForm({ ...form, label: e.target.value })} placeholder="My Tab" />
          </label>
          <label>
            Sort order
            <input type="number" value={form.sort_order} onChange={(e) => setForm({ ...form, sort_order: Number(e.target.value) })} />
          </label>
          <label>
            Icon
            <input value={form.icon} onChange={(e) => setForm({ ...form, icon: e.target.value })} placeholder=" icon name" />
          </label>
          <label className="checkbox">
            <input type="checkbox" checked={form.is_visible} onChange={(e) => setForm({ ...form, is_visible: e.target.checked })} />
            <span>Visible</span>
          </label>
          <button onClick={submit}>Create tab</button>
        </div>
      </div>
      <div className="admin-card">
        <h3>Tabs</h3>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Path</th>
                <th>Label</th>
                <th>Sort</th>
                <th>Visible</th>
                <th>Icon</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>{(tabs || []).map((t) => (
              <tr key={t.id} className="admin-table-row">
                <td className="mono">{t.id}</td>
                <td>{t.path}</td>
                <td>{t.label}</td>
                <td className="center">{t.sort_order}</td>
                <td className="center">{t.is_visible ? 'yes' : 'no'}</td>
                <td>{t.icon || '—'}</td>
                <td className="actions">
                  <button onClick={() => remove(t.id)}>delete</button>
                </td>
              </tr>
            ))}</tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function UsersManager() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  useEffect(() => {
    let cancelled = false;
    get('/admin/users')
      .then((res) => {
        if (!cancelled && res && typeof res === 'object') setUsers((res as { users?: AdminUser[] }).users || []);
      })
      .catch(() => { if (!cancelled) setUsers([]); });
    return () => { cancelled = true; };
  }, []);

  return (
    <div className="admin-section">
      <div className="admin-card">
        <h3>Users</h3>
        <p className="dim">User management from backend.</p>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Username</th>
                <th>Role</th>
                <th>Active</th>
                <th>Locked</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {(users || []).map((u) => (
                <tr key={u.id} className="admin-table-row">
                  <td className="mono">{u.id}</td>
                  <td>{u.username}</td>
                  <td>{typeof u.role === 'string' ? u.role : u.role?.name}</td>
                  <td className="center">{u.is_active ? 'yes' : 'no'}</td>
                  <td className="center">{u.is_locked ? 'yes' : 'no'}</td>
                  <td className="actions">
                    <button>edit</button>
                    <button>delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function RolesManager() {
  const [roles, setRoles] = useState<Role[]>([]);
  useEffect(() => {
    let cancelled = false;
    get('/admin/roles')
      .then((res) => {
        if (!cancelled && res && typeof res === 'object') setRoles((res as { roles?: Role[] }).roles || []);
      })
      .catch(() => { if (!cancelled) setRoles([]); });
    return () => { cancelled = true; };
  }, []);

  return (
    <div className="admin-section">
      <div className="admin-card">
        <h3>Roles</h3>
        <ul className="role-chips">
          {roles.map((r) => (
            <li key={r.id} className="chip">{r.name}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
