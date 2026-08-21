import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import { fileURLToPath } from 'node:url';

const srcPath = (segment = '') =>
  fileURLToPath(new URL(`./src/${segment}`, import.meta.url));

export default defineConfig({
  plugins: [react()],

  resolve: {
    alias: {
      '@': srcPath(),
      '@components': srcPath('components'),
      '@pages': srcPath('pages'),
      '@hooks': srcPath('hooks'),
      '@utils': srcPath('utils'),
      '@lib': srcPath('lib'),
      '@contexts': srcPath('contexts'),
      '@providers': srcPath('providers'),
      '@layouts': srcPath('layouts'),
    },
  },

  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/setupTests.ts'],
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
    css: true,
  },
});
