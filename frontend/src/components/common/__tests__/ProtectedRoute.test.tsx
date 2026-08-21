"""
ProtectedRoute Component Tests

Unit tests for the ProtectedRoute component.
"""

import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import Cookies from 'js-cookie';

// Mock cookies
jest.mock('js-cookie');

// Import component after mocking
import ProtectedRoute, { PublicRoute, AuthLoading } from '../ProtectedRoute';

describe('ProtectedRoute', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render children when authenticated', () => {
    (Cookies.get as jest.Mock).mockReturnValue('test-token');

    render(
      <MemoryRouter initialEntries={['/protected']}>
        <Routes>
          <Route
            path="/protected"
            element={
              <ProtectedRoute>
                <div>Protected Content</div>
              </ProtectedRoute>
            }
          />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });

  it('should redirect to login when not authenticated', () => {
    (Cookies.get as jest.Mock).mockReturnValue(undefined);

    render(
      <MemoryRouter initialEntries={['/protected']}>
        <Routes>
          <Route
            path="/protected"
            element={
              <ProtectedRoute redirectTo="/login">
                <div>Protected Content</div>
              </ProtectedRoute>
            }
          />
          <Route path="/login" element={<div>Login Page</div>} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText('Login Page')).toBeInTheDocument();
  });

  it('should redirect to custom path when not authenticated', () => {
    (Cookies.get as jest.Mock).mockReturnValue(undefined);

    render(
      <MemoryRouter initialEntries={['/protected']}>
        <Routes>
          <Route
            path="/protected"
            element={
              <ProtectedRoute redirectTo="/custom">
                <div>Protected Content</div>
              </ProtectedRoute>
            }
          />
          <Route path="/custom" element={<div>Custom Page</div>} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText('Custom Page')).toBeInTheDocument();
  });

  it('should not require auth when requireAuth is false', () => {
    (Cookies.get as jest.Mock).mockReturnValue(undefined);

    render(
      <MemoryRouter initialEntries={['/public']}>
        <Routes>
          <Route
            path="/public"
            element={
              <ProtectedRoute requireAuth={false}>
                <div>Public Content</div>
              </ProtectedRoute>
            }
          />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText('Public Content')).toBeInTheDocument();
  });
});

describe('PublicRoute', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render children when not authenticated', () => {
    (Cookies.get as jest.Mock).mockReturnValue(undefined);

    render(
      <MemoryRouter initialEntries={['/login']}>
        <Routes>
          <Route
            path="/login"
            element={
              <PublicRoute>
                <div>Login Page</div>
              </PublicRoute>
            }
          />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText('Login Page')).toBeInTheDocument();
  });

  it('should redirect to home when authenticated', () => {
    (Cookies.get as jest.Mock).mockReturnValue('test-token');

    render(
      <MemoryRouter initialEntries={['/login']}>
        <Routes>
          <Route
            path="/login"
            element={
              <PublicRoute redirectTo="/">
                <div>Login Page</div>
              </PublicRoute>
            }
          />
          <Route path="/" element={<div>Home Page</div>} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText('Home Page')).toBeInTheDocument();
  });

  it('should redirect to custom path when authenticated', () => {
    (Cookies.get as jest.Mock).mockReturnValue('test-token');

    render(
      <MemoryRouter initialEntries={['/login']}>
        <Routes>
          <Route
            path="/login"
            element={
              <PublicRoute redirectTo="/dashboard">
                <div>Login Page</div>
              </PublicRoute>
            }
          />
          <Route path="/dashboard" element={<div>Dashboard</div>} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText('Dashboard')).toBeInTheDocument();
  });
});

describe('AuthLoading', () => {
  it('should render loading spinner', () => {
    render(<AuthLoading />);

    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });
});
