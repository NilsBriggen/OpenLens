import React, { Suspense, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider, Spin, theme } from 'antd';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import Cookies from 'js-cookie';

// Layout
import MainLayout from './layouts/MainLayout';
import AuthLayout from './layouts/AuthLayout';

// Pages - Lazy loaded for performance
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
const GraphExplorer = React.lazy(() => import('./pages/GraphExplorer'));
const AIAnalytics = React.lazy(() => import('./pages/AIAnalytics'));
const ScrapingHub = React.lazy(() => import('./pages/ScrapingHub'));
const SecurityCenter = React.lazy(() => import('./pages/SecurityCenter'));
const ThreatIntelligence = React.lazy(() => import('./pages/ThreatIntelligence'));
const Settings = React.lazy(() => import('./pages/Settings'));
const Login = React.lazy(() => import('./pages/Login'));
const Register = React.lazy(() => import('./pages/Register'));
const NotFound = React.lazy(() => import('./pages/NotFound'));

// Components
import LoadingSpinner from './components/common/LoadingSpinner';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 2,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

const App: React.FC = () => {
  const [isDarkMode, setIsDarkMode] = React.useState(false);

  useEffect(() => {
    // Check for dark mode preference
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    setIsDarkMode(savedTheme === 'dark' || (savedTheme === null && prefersDark));
  }, []);

  const toggleTheme = () => {
    const newTheme = !isDarkMode;
    setIsDarkMode(newTheme);
    localStorage.setItem('theme', newTheme ? 'dark' : 'light');
  };

  const isAuthenticated = !!Cookies.get('access_token');

  return (
    <ConfigProvider
      theme={
        algorithm: isDarkMode ? theme.darkAlgorithm : theme.defaultAlgorithm,
        token: {
          colorPrimary: '#1890ff',
          borderRadius: 8,
        },
      }
    >
      <QueryClientProvider client={queryClient}>
        <Router>
          <Suspense fallback={<LoadingSpinner fullScreen />}>
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: isDarkMode ? '#1a1a1a' : '#fff',
                  color: isDarkMode ? '#fff' : '#000',
                },
              }}
            />
            
            <Routes>
              {/* Public Routes */}
              <Route path="/login" element={<AuthLayout><Login /></AuthLayout>} />
              <Route path="/register" element={<AuthLayout><Register /></AuthLayout>} />
              
              {/* Protected Routes */}
              <Route
                path="/"
                element={
                  isAuthenticated ? (
                    <MainLayout toggleTheme={toggleTheme} isDarkMode={isDarkMode}>
                      <Dashboard />
                    </MainLayout>
                  ) : (
                    <Navigate to="/login" replace />
                  )
                }
              />
              
              <Route
                path="/graph"
                element={
                  isAuthenticated ? (
                    <MainLayout toggleTheme={toggleTheme} isDarkMode={isDarkMode}>
                      <GraphExplorer />
                    </MainLayout>
                  ) : (
                    <Navigate to="/login" replace />
                  )
                }
              />
              
              <Route
                path="/ai"
                element={
                  isAuthenticated ? (
                    <MainLayout toggleTheme={toggleTheme} isDarkMode={isDarkMode}>
                      <AIAnalytics />
                    </MainLayout>
                  ) : (
                    <Navigate to="/login" replace />
                  )
                }
              />
              
              <Route
                path="/scraping"
                element={
                  isAuthenticated ? (
                    <MainLayout toggleTheme={toggleTheme} isDarkMode={isDarkMode}>
                      <ScrapingHub />
                    </MainLayout>
                  ) : (
                    <Navigate to="/login" replace />
                  )
                }
              />
              
              <Route
                path="/security"
                element={
                  isAuthenticated ? (
                    <MainLayout toggleTheme={toggleTheme} isDarkMode={isDarkMode}>
                      <SecurityCenter />
                    </MainLayout>
                  ) : (
                    <Navigate to="/login" replace />
                  )
                }
              />
              
              <Route
                path="/threat"
                element={
                  isAuthenticated ? (
                    <MainLayout toggleTheme={toggleTheme} isDarkMode={isDarkMode}>
                      <ThreatIntelligence />
                    </MainLayout>
                  ) : (
                    <Navigate to="/login" replace />
                  )
                }
              />
              
              <Route
                path="/settings"
                element={
                  isAuthenticated ? (
                    <MainLayout toggleTheme={toggleTheme} isDarkMode={isDarkMode}>
                      <Settings />
                    </MainLayout>
                  ) : (
                    <Navigate to="/login" replace />
                  )
                }
              />
              
              {/* 404 */}
              <Route path="*" element={<NotFound />} />
            </Routes>
          </Suspense>
        </Router>
      </QueryClientProvider>
    </ConfigProvider>
  );
};

export default App;
