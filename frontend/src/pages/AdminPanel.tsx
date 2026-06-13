import { useEffect, useState } from 'react';
import { get } from '../services/api';

export default function AdminPanel() {
  const [roles, setRoles] = useState<string[]>([]);

  useEffect(() => {
    get('/admin/roles').then((data: any) => setRoles(data.roles)).catch(() => {});
  }, []);

  return (
    <section style={{ background: '#0b1220ee', border: '1px solid #a78bfa33', borderRadius: 16, padding: 20 }}>
      <h1 style={{ fontSize: 22 }}>Admin Panel</h1>
      <p style={{ color: '#94a3b8' }}>RBAC roles: {roles.join(', ')}</p>
    </section>
  );
}
