/**
 * ProtectedRoute tests.
 */
import React from 'react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';

vi.mock('../../../hooks/useApi', () => ({
  isAuthenticated: vi.fn(() => false),
}));

import { isAuthenticated } from '../../../hooks/useApi';
import ProtectedRoute, { PublicRoute, AuthLoading } from '../ProtectedRoute';

const mockedIsAuthenticated = isAuthenticated as unknown as ReturnType<typeof vi.fn>;

const renderWithRouter = (element: React.ReactElement) =>
  render(
    <MemoryRouter initialEntries={['/protected']}>
      <Routes>
        <Route path="/protected" element={element} />
        <Route path="/login" element={<div>Login page</div>} />
        <Route path="/" element={<div>Home page</div>} />
      </Routes>
    </MemoryRouter>,
  );

beforeEach(() => vi.clearAllMocks());

describe('ProtectedRoute', () => {
  it('renders children when authenticated', () => {
    mockedIsAuthenticated.mockReturnValue(true);
    renderWithRouter(
      <ProtectedRoute>
        <div>Secret content</div>
      </ProtectedRoute>,
    );
    expect(screen.getByText('Secret content')).toBeInTheDocument();
  });

  it('redirects to /login when not authenticated', () => {
    mockedIsAuthenticated.mockReturnValue(false);
    renderWithRouter(
      <ProtectedRoute>
        <div>Secret content</div>
      </ProtectedRoute>,
    );
    expect(screen.queryByText('Secret content')).not.toBeInTheDocument();
    expect(screen.getByText('Login page')).toBeInTheDocument();
  });
});

describe('PublicRoute', () => {
  it('renders children when not authenticated', () => {
    mockedIsAuthenticated.mockReturnValue(false);
    renderWithRouter(
      <PublicRoute>
        <div>Public content</div>
      </PublicRoute>,
    );
    expect(screen.getByText('Public content')).toBeInTheDocument();
  });

  it('redirects home when already authenticated', () => {
    mockedIsAuthenticated.mockReturnValue(true);
    renderWithRouter(
      <PublicRoute>
        <div>Public content</div>
      </PublicRoute>,
    );
    expect(screen.queryByText('Public content')).not.toBeInTheDocument();
    expect(screen.getByText('Home page')).toBeInTheDocument();
  });
});

describe('AuthLoading', () => {
  it('renders a visible loading label (antd 5 drops Spin tip on leaf spinners)', () => {
    render(<AuthLoading />);
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });
});
