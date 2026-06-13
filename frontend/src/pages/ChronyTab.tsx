import { useEffect, useState } from 'react';
import { get } from '../services/api';

export default function ChronyTab() {
  const [status, setStatus] = useState<any>(null);

  useEffect(() => {
    get('/chrony/status').then(setStatus).catch(() => {});
  }, []);

  return (
    <section style={{ background: '#0b1220ee', border: '1px solid #38bdf833', borderRadius: 16, padding: 20 }}>
      <h1 style={{ fontSize: 22 }}>Chrony NTP Dashboard</h1>
      <pre style={{ color: '#94a3b8' }}>{JSON.stringify(status, null, 2)}</pre>
    </section>
  );
}
