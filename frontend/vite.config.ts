import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { visualizer } from 'rollup-plugin-visualizer';
import { fileURLToPath } from 'node:url';

const srcPath = (segment = '') =>
  fileURLToPath(new URL(`./src/${segment}`, import.meta.url));

/** Third-party packages grouped into shared vendor chunks. */
const VENDOR_CHUNKS: Record<string, string> = {
  react: 'vendor',
  'react-dom': 'vendor',
  'react-router-dom': 'vendor',
  antd: 'antd',
  '@ant-design/icons': 'antd',
  '@ant-design/plots': 'charts',
  recharts: 'charts',
  d3: 'charts',
  cytoscape: 'cytoscape',
  'react-cytoscapejs': 'cytoscape',
  'monaco-editor': 'monaco',
  '@monaco-editor/react': 'monaco',
  three: 'three',
  'react-flow-renderer': 'three',
};

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  plugins: [
    react(),
    // Bundle analyzer - only wired up for `npm run build:analyze`, otherwise it
    // would run (and pop open a browser tab) on every dev start and build.
    ...(mode === 'analyze'
      ? [
          visualizer({
            open: true,
            gzipSize: true,
            brotliSize: true,
            filename: 'bundle-analysis.html',
          }),
        ]
      : []),
  ],

  // The app reads its configuration through `import.meta.env.REACT_APP_*`,
  // so Vite has to expose that prefix in addition to its own.
  envPrefix: ['VITE_', 'REACT_APP_'],

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

  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        ws: true,
      },
    },
  },

  build: {
    // Enable code splitting. Vite 8 bundles with rolldown, which only accepts
    // the function form of manualChunks.
    rollupOptions: {
      output: {
        manualChunks(id: string) {
          const normalized = id.replace(/\\/g, '/');
          if (!normalized.includes('/node_modules/')) return;

          // Last node_modules segment wins, so nested deps map to their own package.
          const match = /\/node_modules\/(@[^/]+\/[^/]+|[^/]+)/g;
          let pkg: string | undefined;
          for (let m = match.exec(normalized); m; m = match.exec(normalized)) {
            pkg = m[1];
          }

          return pkg ? VENDOR_CHUNKS[pkg] : undefined;
        },
      },
    },

    // Optimize chunk size
    chunkSizeWarningLimit: 1000,

    // Minify output. Vite 8 minifies with oxc; the esbuild minifier is no
    // longer bundled and naming it here fails the build.
    minify: true,

    // Generate source maps for debugging
    sourcemap: true,
  },

  // Optimize dependencies
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      'antd',
      '@ant-design/icons',
      '@tanstack/react-query',
      'axios',
      'framer-motion',
      'cytoscape',
      'react-cytoscapejs',
    ],
    exclude: [
      // These are large and should be code-split
      'monaco-editor',
      'three',
    ],
  },

  // CSS optimization
  css: {
    preprocessorOptions: {
      less: {
        javascriptEnabled: true,
      },
    },
  },
}));
