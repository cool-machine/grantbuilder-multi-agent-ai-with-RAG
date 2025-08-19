import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { LanguageProvider } from './contexts/LanguageContext';
import { GrantProvider } from './contexts/GrantContext';
import Header from './components/layout/Header';
import Footer from './components/layout/Footer';
import HomePage from './pages/HomePage';
import GrantsPage from './pages/GrantsPage';
import GrantDetailPage from './pages/GrantDetailPage';
import DashboardPage from './pages/DashboardPage';
import AdminPage from './pages/AdminPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import GrantAnalysisPage from './pages/GrantAnalysisPage';
import DocumentAnalysisPage from './pages/DocumentAnalysisPage';
import FillApplicationPage from './pages/FillApplicationPage';

function App() {
  return (
    <LanguageProvider>
      <AuthProvider>
        <GrantProvider>
          <Router basename="/grantseeker-front">
            <div className="min-h-screen bg-gray-50 flex flex-col">
              <Header />
              <main className="flex-1">
                <Routes>
                  <Route index element={<HomePage />} />
                  <Route path="/" element={<HomePage />} />
                  <Route path="/grants" element={<GrantsPage />} />
                  <Route path="/grants/:id" element={<GrantDetailPage />} />
                  <Route path="/dashboard" element={<DashboardPage />} />
                  <Route path="/admin" element={<AdminPage />} />
                  <Route path="/login" element={<LoginPage />} />
                  <Route path="/register" element={<RegisterPage />} />
                  <Route path="/ai-analysis" element={<GrantAnalysisPage />} />
                  <Route path="/document-analysis" element={<DocumentAnalysisPage />} />
                  <Route path="/fill-application" element={<FillApplicationPage />} />
                  <Route path="/fill-application/:grantId" element={<FillApplicationPage />} />
                </Routes>
              </main>
              <Footer />
            </div>
          </Router>
        </GrantProvider>
      </AuthProvider>
    </LanguageProvider>
  );
}

export default App;