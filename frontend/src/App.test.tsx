/**
 * App smoke test: the tree renders without throwing and lands on the login
 * page when unauthenticated. (Replaces the CRA "learn react" boilerplate.)
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from './App';

describe('App', () => {
  it('renders and redirects to the login page when unauthenticated', async () => {
    render(<App />);
    expect(await screen.findByText(/Welcome to OpenLens/i, undefined,
      { timeout: 5000 })).toBeInTheDocument();
  });
});
