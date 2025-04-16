
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";

export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 8080,
  },
  plugins: [
    react(),
    mode === 'development' &&
    componentTagger(),
  ].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    deps: {
      external: ['@testing-library/react']
    }
  },
  build: {
    sourcemap: true,
    outDir: 'static',
    rollupOptions: {
      external: [
        'api/main.py',
        'server.js',
        'setup.py',
        'api/__init__.py',
        'requirements.txt',
        'api/requirements.txt'
      ]
    }
  }
}));
