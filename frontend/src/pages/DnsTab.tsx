import { useState } from 'react';
import { post } from '../services/api';

export default function DnsTab() {
  const [domain, setDomain] = useState('');
  const [result, setResult] = useState<any>(null);

  const run = async () => {
    const res = await post('/tools/dns/benchmark', { domain });
    setResult(res);
  };

  return (
    <section style={{ background: '#0b1220ee', border: '1px solid #facc1533', borderRadius: 16, padding: 20 }}>
      <h1 style={{ fontSize: 22 }}>DNS Resolver Tools</h1>
      <input value={domain} onChange={(e) => setDomain(e.target.value)} placeholder="example.com" />
      <button onClick={run} style={{ marginLeft: 8 }}>Run</button>
      <pre style={{ color: '#94a3b8', marginTop: 12 }}>{JSON.stringify(result, null, 2)}</pre>
    </section>
  );
}
