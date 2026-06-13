import { useEffect, useState } from 'react';
import { get } from '../services/api';

export default function LDAPTab() {
  const [users, setUsers] = useState<any>(null);

  useEffect(() => {
    get('/ldap/users').then((data: any) => setUsers(data.users)).catch(() => {});
  }, []);

  return (
    <section style={{ background: '#0b1220ee', border: '1px solid #fbbf2433', borderRadius: 16, padding: 20 }}>
      <h1 style={{ fontSize: 22 }}>LDAP / AD Integration</h1>
      <pre style={{ color: '#94a3b8' }}>{JSON.stringify(users, null, 2)}</pre>
    </section>
  );
}
