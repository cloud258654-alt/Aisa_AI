import { HashRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/common/Layout';
import DashboardPage from './pages/DashboardPage';
import CustomersPage from './pages/CustomersPage';
import ContainersPage from './pages/ContainersPage';
import RentalsPage from './pages/RentalsPage';
import CustomerLedgersPage from './pages/CustomerLedgersPage';
import ManagementLedgersPage from './pages/ManagementLedgersPage';
import SettingsPage from './pages/SettingsPage';
import LoginPage from './pages/LoginPage';
import { useState, useEffect } from 'react';
import { onAuthStateChanged, User } from 'firebase/auth';
import { auth } from './services/firebase/firebase';

export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [checkingAuth, setCheckingAuth] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
      setCheckingAuth(false);
    });
    return () => unsubscribe();
  }, []);

  if (checkingAuth) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950 text-indigo-400">
        <div className="flex flex-col items-center gap-3">
          <span className="w-8 h-8 border-4 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin"></span>
          <span className="text-xs text-slate-400">正在確認驗證狀態...</span>
        </div>
      </div>
    );
  }

  if (!user) {
    return <LoginPage />;
  }

  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/customers" element={<CustomersPage />} />
          <Route path="/containers" element={<ContainersPage />} />
          <Route path="/rentals" element={<RentalsPage />} />
          <Route path="/customer-ledgers" element={<CustomerLedgersPage />} />
          <Route path="/management-ledgers" element={<ManagementLedgersPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="*" element={<DashboardPage />} />
        </Routes>
      </Layout>
    </Router>
  );
}
