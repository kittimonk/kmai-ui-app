
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
        // Backend files
        '/backend/**/*',
        '/backend/*',
        'backend/**/*',
        'backend/*',
        '**/backend/**',
        // Deployment scripts
        'server.js',
        'setup.py',
        '.deployment',
        'requirements.txt',
        'backend/requirements.txt',
        'kmai_ent03_ui_app.egg-info/**/*',
        'kmai_ent03_ui_app.egg-info/*',
        'startup.sh',
        'web.config',
        'deploy.sh',
        'build-local.sh',
        // Additional files to exclude
        'MANIFEST.in',
        '.env',
        '.env.dev',
        '.gitignore',
        'README.md',
        'src/components/ai-app.yml',
        'CODEOWNERS',
        'EDP.yml',
        '.github/**/*',
        '**/node_modules/**'
      ]
    }
  }
}));
