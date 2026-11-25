import path from 'path';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Hybrid IDE config - optimized for Flask serving and pywebview
export default defineConfig({
  plugins: [react()],
  base: './',  // CRITICAL - relative paths for Flask
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,  // Smaller build
    rollupOptions: {
      output: {
        manualChunks: undefined  // Single bundle for simplicity
      }
    }
  },
  server: {
    port: Number(process.env.PORT) || 3000,
    host: '0.0.0.0',
    strictPort: false
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, '.'),
    }
  }
});
