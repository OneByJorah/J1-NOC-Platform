import { useEffect, useState } from 'react';
import { get } from '../services/api';

export default function SNMPTab() {
  const [devices, setDevices] = useState<any>(null);

  useEffect(() => {
    get('/snmp/discover?subnet=192.0.2.0/24').then((data: any) => setDevices(data)).catch(() => {});
  }, []);

  return (
    <section style={{ background: '#0b1220ee', border: '1px solid #f9731633', borderRadius: 16, padding: 20 }}>
      <h1 style={{ fontSize: 22 }}>SNMP Auto-Discovery</h1>
      <pre style={{ color: '#94a3b8' }}>{JSON.stringify(devices, null, 2)}</pre>
    </section>
  );
}
