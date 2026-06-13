import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import DashboardHome from './pages/DashboardHome';
import ChronyTab from './pages/ChronyTab';
import TicketsTab from './pages/TicketsTab';
import DnsTab from './pages/DnsTab';
import AdminPanel from './pages/AdminPanel';
import AIAssistant from './pages/AIAssistant';
import LDAPTab from './pages/LDAPTab';
import SNMPTab from './pages/SNMPTab';

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<DashboardHome />} />
        <Route path="/ldap" element={<LDAPTab />} />
        <Route path="/snmp" element={<SNMPTab />} />
        <Route path="/chrony" element={<ChronyTab />} />
        <Route path="/tickets" element={<TicketsTab />} />
        <Route path="/dns" element={<DnsTab />} />
        <Route path="/admin" element={<AdminPanel />} />
        <Route path="/ai" element={<AIAssistant />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
}
