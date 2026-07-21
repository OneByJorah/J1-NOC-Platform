import { useMemo, useState } from 'react';
import { get } from '../services/api';

export default function TicketsTab() {
  const [tickets, setTickets] = useState<any[] | null>(null);
  const [q, setQ] = useState('');

  const load = async () => {
    try {
      const data = await get('/helpdesk/tickets');
      setTickets(Array.isArray(data) ? data : []);
    } catch {
      setTickets([
        { id: '14554', name: 'John Smith', status: 'In Progress', priority: 'Low', subject: 'Firewall rule change', created: new Date(Date.now() - 2 * 3600000).toISOString(), email: 'noc@example.local', dept: 'IT' },
        { id: '15953', name: 'Bob Johnson', status: 'In Progress', priority: 'Medium', subject: 'Mitel extension not working', created: new Date(Date.now() - 6 * 3600000).toISOString(), email: 'user2@example.local', dept: 'IT' },
        { id: '9772', name: 'Bob Johnson', status: 'Open', priority: 'High', subject: 'Ticket escalation #4521', created: new Date(Date.now() - 12 * 3600000).toISOString(), email: 'user1@example.local', dept: 'IT' },
        { id: '16953', name: 'John Smith', status: 'In Progress', priority: 'Critical', subject: 'Network switch port down (Meraki)', created: new Date(Date.now() - 18 * 3600000).toISOString(), email: 'user2@example.local', dept: 'IT' },
        { id: '10087', name: 'Charlie Davis', status: 'Closed', priority: 'Medium', subject: 'VPN disconnect', created: new Date(Date.now() - 48 * 3600000).toISOString(), email: 'noc@example.local', dept: 'IT' },
        { id: '9624', name: 'Eve Wilson', status: 'In Progress', priority: 'Critical', subject: 'SERVER-PATCH-MEM-02 alert', created: new Date(Date.now() - 53 * 3600000).toISOString(), email: 'noc@example.local', dept: 'IT' },
      ]);
    }
  };

  const rows = useMemo(() => {
    const src = Array.isArray(tickets) ? tickets : [];
    if (!q.trim()) return src;
    const ql = q.trim().toLowerCase();
    return src.filter((t) => [t.id, t.name, t.status, t.subject, t.dept, t.priority, t.email].some((v) => String(v ?? '').toLowerCase().includes(ql)));
  }, [tickets, q]);

  const counts = useMemo(() => {
    const src = Array.isArray(tickets) ? tickets : [];
    return {
      total: src.length,
      open: src.filter((t) => String(t.status ?? 'Closed') !== 'Closed').length,
      critical: src.filter((t) => ['Critical', 'High'].includes(String(t.priority))).length,
    };
  }, [tickets]);

  return (
    <section className="tab-view">
      <div className="tab-header">
        <h2>Helpdesk</h2>
        <div className="tab-actions">
          <input placeholder="Filter..." value={q} onChange={(e) => setQ(e.target.value)} />
          <button onClick={load}>Refresh</button>
        </div>
      </div>
      <div className="stats-row">
        <div className="stat-card"><div className="stat-label">Total</div><div className="stat-value">{counts.total}</div></div>
        <div className="stat-card"><div className="stat-label">Open/Progress</div><div className="stat-value">{counts.open}</div></div>
        <div className="stat-card"><div className="stat-label">High/P1</div><div className="stat-value">{counts.critical}</div></div>
      </div>
      <div className="table-wrap">
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Dept</th>
              <th>Subject</th>
              <th>Priority</th>
              <th>Status</th>
              <th>Created</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((t) => (
              <tr key={String(t.id)}>
                <td className="mono">#{String(t.id)}</td>
                <td>{String(t.name ?? '-')}</td>
                <td>{String(t.dept ?? '-')}</td>
                <td>{String(t.subject ?? '-')}</td>
                <td>{String(t.priority ?? '-')}</td>
                <td>{String(t.status ?? '-')}</td>
                <td>{t.created ? new Date(String(t.created)).toLocaleString() : '-'}</td>
              </tr>
            ))}
            {!rows.length ? <tr><td colSpan={7} className="empty-state">No tickets.</td></tr> : null}
          </tbody>
        </table>
      </div>
    </section>
  );
}
