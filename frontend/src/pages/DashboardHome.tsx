import { useEffect, useState } from 'react';
import { get } from '../services/api';

export default function DashboardHome() {
  const [data, setData] = useState<{ clients_online: number; alerts: number; score: number } | null>(null);

  useEffect(() => {
    get('/dashboard/overview')
      .then(setData)
      .catch(() => {});
  }, []);

  return (
    <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 20 }}>
      <Stat title="Clients Online" value={data?.clients_online ?? '—'} accent="#38bdf8" />
      <Stat title="Alerts" value={data?.alerts ?? '—'} accent="#ef4444" />
      <Stat title="Health Score" value={data?.score ?? '—'} accent="#22c55e" />
    </section>
  );
}

function Stat({ title, value, accent }: { title: string; value: number | string; accent: string }) {
  return (
    <div style={{ background: '#0b1220ee', border: `1px solid ${accent}44`, borderRadius: 16, padding: 18 }}>
      <div style={{ color: '#94a3b8', marginBottom: 4 }}>{title}</div>
      <div style={{ fontSize: 28, fontWeight: 700, color: '#e5e7eb' }}>{value}</div>
    </div>
  );
}
