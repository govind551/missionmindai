import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Navbar } from './components/common/Navbar';
import { Sidebar } from './components/common/Sidebar';

// Pages
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { DashboardPage } from './pages/DashboardPage';
import { ResearchAssistantPage } from './pages/ResearchAssistantPage';
import { SimilarFailuresPage } from './pages/SimilarFailuresPage';
import { FailureChainPage } from './pages/FailureChainPage';
import { DocumentLibraryPage } from './pages/DocumentLibraryPage';
import { ResearchReportsPage } from './pages/ResearchReportsPage';
import { SettingsPage } from './pages/SettingsPage';
import { AdminPage } from './pages/AdminPage';

const AppLayout: React.FC = () => {
  return (
    <div className="min-h-screen bg-space-950 flex flex-col selection:bg-cosmic-purple selection:text-white">
      <Navbar />
      <div className="flex-1 flex overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto bg-space-950">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Landing & Authentication */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Application Layout Routes */}
          <Route element={<AppLayout />}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/assistant" element={<ResearchAssistantPage />} />
            <Route path="/similar-failures" element={<SimilarFailuresPage />} />
            <Route path="/failure-chain" element={<FailureChainPage />} />
            <Route path="/documents" element={<DocumentLibraryPage />} />
            <Route path="/reports" element={<ResearchReportsPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="/admin" element={<AdminPage />} />
          </Route>

          {/* Catch-all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
