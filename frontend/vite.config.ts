import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { visualizer } from 'rollup-plugin-visualizer';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    // Bundle analyzer - run with `npm run build -- --analyze`
    visualizer({
      open: true,
      gzipSize: true,
      brotliSize: true,
      filename: 'bundle-analysis.html',
    }) as any,
  ],
  
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@pages': path.resolve(__dirname, './src/pages'),
      '@hooks': path.resolve(__dirname, './src/hooks'),
      '@utils': path.resolve(__dirname, './src/utils'),
      '@lib': path.resolve(__dirname, './src/lib'),
      '@contexts': path.resolve(__dirname, './src/contexts'),
      '@providers': path.resolve(__dirname, './src/providers'),
      '@layouts': path.resolve(__dirname, './src/layouts'),
    },
  },
  
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
  
  build: {
    // Enable code splitting
    rollupOptions: {
      output: {
        manualChunks: {
          // Split vendor chunks
          vendor: ['react', 'react-dom', 'react-router-dom'],
          antd: ['antd', '@ant-design/icons'],
          charts: ['@ant-design/charts', '@ant-design/plots', 'recharts', 'd3'],
          cytoscape: ['cytoscape', 'react-cytoscapejs'],
          monaco: ['@monaco-editor/react', 'monaco-editor'],
          three: ['three', 'react-flow-renderer'],
          // Split feature chunks
          graph: ['./src/components/GraphVisualization.tsx', './src/components/ConnectedGraphVisualization.tsx'],
          ai: ['./src/components/AIChatAssistant.tsx'],
          scraping: ['./src/pages/ScrapingHub.tsx'],
          threat: ['./src/pages/ThreatIntelligence.tsx'],
          security: ['./src/pages/SecurityCenter.tsx'],
        },
      },
    },
    
    // Optimize chunk size
    chunkSizeWarningLimit: 1000,
    
    // Minify output
    minify: 'esbuild',
    
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
});
