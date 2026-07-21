import { HashRouter as Router, Route, Routes } from 'react-router-dom';
import { SessionProvider } from './contexts/SessionContext';
import { useSession } from './hooks/useSession';
import AppShell from './components/layout/AppShell';
import DashboardPage from './pages/DashboardPage';
import CustomersPage from './pages/CustomersPage';
import ContainersPage from './pages/ContainersPage';
import RentalsPage from './pages/RentalsPage';
import CustomerLedgersPage from './pages/CustomerLedgersPage';
import ManagementLedgersPage from './pages/ManagementLedgersPage';
import SettingsPage from './pages/SettingsPage';
import LoginPage from './pages/LoginPage';
import ContractsPage from './pages/ContractsPage';
import InvoicesPage from './pages/InvoicesPage';
import TerminationPage from './pages/TerminationPage';
import RatePlansPage from './pages/RatePlansPage';

function AccessGate() {
  const { isAuthenticated, loading, error, logout } = useSession();
  
  if (loading) {
    return <div className="min-h-screen flex items-center justify-center bg-surface-page text-text-secondary">正在確認登入狀態...</div>;
  }
  
  if (!isAuthenticated) {
    return <LoginPage />;
  }
  
  if (error) {
    return (
      <div className="min-h-screen flex flex-col gap-4 items-center justify-center bg-surface-page text-status-danger">
        <p>{error}</p>
        <button onClick={() => void logout()} className="rounded bg-status-danger px-4 py-2 text-white font-medium">
          返回登入
        </button>
      </div>
    );
  }
  
  return (
    <Router>
      <AppShell>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/customers" element={<CustomersPage />} />
          <Route path="/containers" element={<ContainersPage />} />
          <Route path="/rentals" element={<RentalsPage />} />
          <Route path="/contracts" element={<ContractsPage />} />
          <Route path="/invoices" element={<InvoicesPage />} />
          <Route path="/termination" element={<TerminationPage />} />
          <Route path="/rate-plans" element={<RatePlansPage />} />
          <Route path="/customer-ledgers" element={<CustomerLedgersPage />} />
          <Route path="/management-ledgers" element={<ManagementLedgersPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="*" element={<DashboardPage />} />
        </Routes>
      </AppShell>
    </Router>
  );
}

export default function App() {
  return (
    <SessionProvider>
      <AccessGate />
    </SessionProvider>
  );
}
