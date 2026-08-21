"""
ProtectedRoute Component

Handles authentication checks and redirects for protected routes.
"""

import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { Spin } from 'antd';
import { isAuthenticated } from '../../hooks/useApi';

interface ProtectedRouteProps {
  children: React.ReactNode;
  redirectTo?: string;
  requireAuth?: boolean;
}

/**
 * ProtectedRoute - Wraps routes that require authentication
 * 
 * @param children - The component to render if authenticated
 * @param redirectTo - Where to redirect if not authenticated (default: /login)
 * @param requireAuth - Whether authentication is required (default: true)
 */
export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  redirectTo = '/login',
  requireAuth = true,
}) => {
  const location = useLocation();
  const authenticated = isAuthenticated();

  // Show loading state while checking authentication
  if (requireAuth && !authenticated) {
    return <Navigate to={redirectTo} state={{ from: location }} replace />;
  }

  // If route doesn't require auth but user is authenticated, redirect to dashboard
  if (!requireAuth && authenticated) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

/**
 * PublicRoute - Wraps routes that should only be accessible when NOT authenticated
 * (e.g., login, register pages)
 */
export const PublicRoute: React.FC<ProtectedRouteProps> = ({
  children,
  redirectTo = '/',
}) => {
  const authenticated = isAuthenticated();

  if (authenticated) {
    return <Navigate to={redirectTo} replace />;
  }

  return <>{children}</>;
};

/**
 * AuthLoading - Shows loading spinner while checking auth state
 */
export const AuthLoading: React.FC = () => {
  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
    }}>
      <Spin size="large" tip="Loading..." />
    </div>
  );
};

export default ProtectedRoute;
