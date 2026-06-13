import { Outlet, Link } from 'react-router-dom';

export default function Layout() {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <header style={{ borderBottom: '1px solid #334155', padding: '14px 18px', display: 'flex', gap: 18, alignItems: 'center', justifyContent: 'space-between' }}>
        <strong style={{ letterSpacing: 1 }}>J1 NOC Platform</strong>
        <nav style={{ display: 'flex', gap: 12 }}>
          <Link to="/">Overview</Link>
          <Link to="/ldap">LDAP</Link>
          <Link to="/snmp">SNMP</Link>
          <Link to="/chrony">Chrony</Link>
          <Link to="/tickets">Tickets</Link>
          <Link to="/dns">DNS</Link>
          <Link to="/admin">Admin</Link>
          <Link to="/ai">AI</Link>
        </nav>
      </header>
      <main style={{ padding: 20, flex: 1 }}>
        <Outlet />
      </main>
    </div>
  );
}
