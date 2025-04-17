
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
        '/backend/**/*',
        '/backend/*',
        'backend/**/*',
        'server.js',
        'setup.py',
        '.deployment',
        'requirements.txt',
        'backend/requirements.txt',
        'MANIFEST.in',
        'kmai_ent03_ui_app.egg-info/**/*',
        'startup.sh',
        'web.config',
        'deploy.sh',
        'build-local.sh'
      ]
    }
  }
}));
