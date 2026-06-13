import { useEffect, useState } from 'react';
import { get } from '../services/api';

export default function AIAssistant() {
  const [status, setStatus] = useState<any>(null);

  useEffect(() => {
    get('/ai/assistant/status').then(setStatus).catch(() => {});
  }, []);

  return (
    <section style={{ background: '#0b1220ee', border: '1px solid #34d39933', borderRadius: 16, padding: 20 }}>
      <h1 style={{ fontSize: 22 }}>AI Assistant</h1>
      <pre style={{ color: '#94a3b8' }}>{JSON.stringify(status, null, 2)}</pre>
    </section>
  );
}
