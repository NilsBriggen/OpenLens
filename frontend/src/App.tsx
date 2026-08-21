import React, { Suspense, useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { FloatButton, Badge, theme } from 'antd';
import { RobotOutlined, BellOutlined, QuestionCircleOutlined } from '@ant-design/icons';
import Cookies from 'js-cookie';

// Providers
import AppProvider from './providers/AppProvider';

// Layout
import MainLayout from './layouts/MainLayout';
import AuthLayout from './layouts/AuthLayout';

// Components
import LoadingSpinner from './components/common/LoadingSpinner';
import ProtectedRoute from './components/common/ProtectedRoute';
import AIChatAssistant from './components/AIChatAssistant';
import NotificationCenter from './components/NotificationCenter';

// Pages - Lazy loaded for performance
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
const RealTimeDashboard = React.lazy(() => import('./pages/RealTimeDashboard'));
const GraphExplorer = React.lazy(() => import('./pages/GraphExplorer'));
const AIAnalytics = React.lazy(() => import('./pages/AIAnalytics'));
const ScrapingHub = React.lazy(() => import('./pages/ScrapingHub'));
const SecurityCenter = React.lazy(() => import('./pages/SecurityCenter'));
const ThreatIntelligence = React.lazy(() => import('./pages/ThreatIntelligence'));
const Settings = React.lazy(() => import('./pages/Settings'));
const Login = React.lazy(() => import('./pages/Login'));
const Register = React.lazy(() => import('./pages/Register'));
const NotFound = React.lazy(() => import('./pages/NotFound'));

// Track page for AI context
const PageTracker: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const location = useLocation();
  const [currentPage, setCurrentPage] = useState<string>('dashboard');

  useEffect(() => {
    const path = location.pathname;
    const pageMap: Record<string, string> = {
      '/': 'dashboard',
      '/dashboard': 'dashboard',
      '/realtime': 'realtime',
      '/graph': 'graph',
      '/ai': 'ai',
      '/scraping': 'scraping',
      '/security': 'security',
      '/threat': 'threat',
      '/settings': 'settings',
    };
    setCurrentPage(pageMap[path] || 'dashboard');
  }, [location.pathname]);

  return React.cloneElement(React.Children.only(children) as React.ReactElement, {
    currentPage,
  });
};

const AppContent: React.FC = () => {
  const [aiAssistantVisible, setAiAssistantVisible] = useState(false);
  const [notificationCenterVisible, setNotificationCenterVisible] = useState(false);
  const [unreadNotifications, setUnreadNotifications] = useState(0);
  const location = useLocation();

  // Check for notifications on route change
  useEffect(() => {
    // In production, this would fetch from the API
    // For now, we'll use a mock value
    const mockNotifications = Math.floor(Math.random() * 10);
    setUnreadNotifications(mockNotifications);
  }, [location.pathname]);

  return (
    <>
      <Suspense fallback={<LoadingSpinner fullScreen />}>
        <Routes>
          {/* Public Routes - Only accessible when NOT authenticated */}
          <Route
            path="/login"
            element={
              <PublicRoute>
                <AuthLayout>
                  <Login />
                </AuthLayout>
              </PublicRoute>
            }
          />
          <Route
            path="/register"
            element={
              <PublicRoute>
                <AuthLayout>
                  <Register />
                </AuthLayout>
              </PublicRoute>
            }
          />

          {/* Protected Routes - Require authentication */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <PageTracker>
                  {(props: any) => (
                    <MainLayout>
                      <Dashboard {...props} />
                    </MainLayout>
                  )}
                </PageTracker>
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <PageTracker>
                  {(props: any) => (
                    <MainLayout>
                      <Dashboard {...props} />
                    </MainLayout>
                  )}
                </PageTracker>
              </ProtectedRoute>
            }
          />
          <Route
            path="/realtime"
            element={
              <ProtectedRoute>
                <PageTracker>
                  {(props: any) => (
                    <MainLayout>
                      <RealTimeDashboard {...props} />
                    </MainLayout>
                  )}
                </PageTracker>
              </ProtectedRoute>
            }
          />
          <Route
            path="/graph"
            element={
              <ProtectedRoute>
                <PageTracker>
                  {(props: any) => (
                    <MainLayout>
                      <GraphExplorer {...props} />
                    </MainLayout>
                  )}
                </PageTracker>
              </ProtectedRoute>
            }
          />
          <Route
            path="/ai"
            element={
              <ProtectedRoute>
                <PageTracker>
                  {(props: any) => (
                    <MainLayout>
                      <AIAnalytics {...props} />
                    </MainLayout>
                  )}
                </PageTracker>
              </ProtectedRoute>
            }
          />
          <Route
            path="/scraping"
            element={
              <ProtectedRoute>
                <PageTracker>
                  {(props: any) => (
                    <MainLayout>
                      <ScrapingHub {...props} />
                    </MainLayout>
                  )}
                </PageTracker>
              </ProtectedRoute>
            }
          />
          <Route
            path="/security"
            element={
              <ProtectedRoute>
                <PageTracker>
                  {(props: any) => (
                    <MainLayout>
                      <SecurityCenter {...props} />
                    </MainLayout>
                  )}
                </PageTracker>
              </ProtectedRoute>
            }
          />
          <Route
            path="/threat"
            element={
              <ProtectedRoute>
                <PageTracker>
                  {(props: any) => (
                    <MainLayout>
                      <ThreatIntelligence {...props} />
                    </MainLayout>
                  )}
                </PageTracker>
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <ProtectedRoute>
                <PageTracker>
                  {(props: any) => (
                    <MainLayout>
                      <Settings {...props} />
                    </MainLayout>
                  )}
                </PageTracker>
              </ProtectedRoute>
            }
          />

          {/* 404 */}
          <Route path="*" element={<NotFound />} />
        </Routes>

        {/* AI Chat Assistant - Available on all authenticated pages */}
        {Cookies.get('access_token') && (
          <>
            <AIChatAssistant
              visible={aiAssistantVisible}
              onClose={() => setAiAssistantVisible(false)}
              context={location.pathname}
            />

            <NotificationCenter
              visible={notificationCenterVisible}
              onClose={() => setNotificationCenterVisible(false)}
            />

            {/* Float Buttons */}
            <FloatButton.Group
              trigger="hover"
              type="primary"
              icon={<RobotOutlined />}
              style={{ right: 24, bottom: 100 }}
              onClick={() => setAiAssistantVisible(true)}
              tooltip="AI Assistant"
            />

            <FloatButton
              icon={<Badge count={unreadNotifications}><BellOutlined /></Badge>}
              type="default"
              style={{ right: 24, bottom: 180 }}
              onClick={() => setNotificationCenterVisible(true)}
              tooltip="Notifications"
            />

            <FloatButton
              icon={<QuestionCircleOutlined />}
              type="default"
              style={{ right: 24, bottom: 260 }}
              tooltip="Help"
            />
          </>
        )}
      </Suspense>
    </>
  );
};

// PublicRoute component for routes that should redirect if authenticated
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const authenticated = !!Cookies.get('access_token');
  
  if (authenticated) {
    return <Navigate to="/" replace />;
  }
  
  return <>{children}</>;
};

const App: React.FC = () => {
  return (
    <AppProvider>
      <Router>
        <AppContent />
      </Router>
    </AppProvider>
  );
};

export default App;
