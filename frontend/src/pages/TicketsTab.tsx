import { useEffect, useState } from 'react';
import { get } from '../services/api';

export default function TicketsTab() {
  const [tickets, setTickets] = useState<any>(null);

  useEffect(() => {
    get('/osticket/tickets').then(setTickets).catch(() => {});
  }, []);

  return (
    <section style={{ background: '#0b1220ee', border: '1px solid #f472b633', borderRadius: 16, padding: 20 }}>
      <h1 style={{ fontSize: 22 }}>osTicket / Helpdesk</h1>
      <pre style={{ color: '#94a3b8' }}>{JSON.stringify(tickets, null, 2)}</pre>
    </section>
  );
}
