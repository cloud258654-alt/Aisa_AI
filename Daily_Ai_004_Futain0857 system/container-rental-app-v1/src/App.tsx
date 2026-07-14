import { HashRouter as Router, Route, Routes } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { useAuth } from './hooks/useAuth';
import Layout from './components/common/Layout';
import DashboardPage from './pages/DashboardPage';
import CustomersPage from './pages/CustomersPage';
import ContainersPage from './pages/ContainersPage';
import RentalsPage from './pages/RentalsPage';
import CustomerLedgersPage from './pages/CustomerLedgersPage';
import ManagementLedgersPage from './pages/ManagementLedgersPage';
import SettingsPage from './pages/SettingsPage';
import LoginPage from './pages/LoginPage';
import PermissionGuard from './components/auth/PermissionGuard';

function AccessGate() {
  const { user, loading, error, logout } = useAuth();
  if (loading) return <div className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-400">正在確認帳號與權限...</div>;
  if (!user) return <LoginPage />;
  if (error) return <div className="min-h-screen flex flex-col gap-4 items-center justify-center bg-slate-950 text-rose-300"><p>{error}</p><button onClick={() => void logout()} className="rounded bg-rose-600 px-4 py-2 text-white">登出</button></div>;
  return <Router><Layout><Routes>
    <Route path="/" element={<DashboardPage />} />
    <Route path="/customers" element={<CustomersPage />} />
    <Route path="/containers" element={<ContainersPage />} />
    <Route path="/rentals" element={<RentalsPage />} />
    <Route path="/customer-ledgers" element={<CustomerLedgersPage />} />
    <Route path="/management-ledgers" element={<ManagementLedgersPage />} />
    <Route path="/settings" element={<PermissionGuard permission="settings:read"><SettingsPage /></PermissionGuard>} />
    <Route path="*" element={<DashboardPage />} />
  </Routes></Layout></Router>;
}
export default function App() { return <AuthProvider><AccessGate /></AuthProvider>; }
