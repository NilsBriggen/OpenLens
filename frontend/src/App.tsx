import React, { Suspense, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Spin, FloatButton, Badge, theme } from 'antd';
import { RobotOutlined, BellOutlined, QuestionCircleOutlined } from '@ant-design/icons';
import Cookies from 'js-cookie';

// Providers
import AppProvider from './providers/AppProvider';

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
import AIChatAssistant from './components/AIChatAssistant';
import NotificationCenter from './components/NotificationCenter';

const App: React.FC = () => {
  const [aiAssistantVisible, setAiAssistantVisible] = useState(false);
  const [notificationCenterVisible, setNotificationCenterVisible] = useState(false);
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [unreadNotifications, setUnreadNotifications] = useState(5);

  const isAuthenticated = !!Cookies.get('access_token');

  // Update current page based on route
  const handleRouteChange = (path: string) => {
    const pageMap: Record<string, string> = {
      '/': 'dashboard',
      '/graph': 'graph',
      '/ai': 'ai',
      '/scraping': 'scraping',
      '/security': 'security',
      '/threat': 'threat',
      '/settings': 'settings',
    };
    setCurrentPage(pageMap[path] || 'dashboard');
  };

  return (
    <AppProvider>
      <Router>
        <Suspense fallback={<LoadingSpinner fullScreen />}>
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<AuthLayout><Login /></AuthLayout>} />
            <Route path="/register" element={<AuthLayout><Register /></AuthLayout>} />
            
            {/* Protected Routes */}
            <Route
              path="/"
              element={
                isAuthenticated ? (
                  <MainLayout onRouteChange={handleRouteChange}>
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
                  <MainLayout onRouteChange={handleRouteChange}>
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
                  <MainLayout onRouteChange={handleRouteChange}>
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
                  <MainLayout onRouteChange={handleRouteChange}>
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
                  <MainLayout onRouteChange={handleRouteChange}>
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
                  <MainLayout onRouteChange={handleRouteChange}>
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
                  <MainLayout onRouteChange={handleRouteChange}>
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

          {/* AI Chat Assistant - Available on all pages */}
          {isAuthenticated && (
            <>
              <AIChatAssistant
                visible={aiAssistantVisible}
                onClose={() => setAiAssistantVisible(false)}
                context={currentPage}
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
      </Router>
    </AppProvider>
  );
};

export default App;
