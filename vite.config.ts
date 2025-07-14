
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";

// Try to import componentTagger, but don't fail if it's missing
let componentTagger;
try {
  const lovableTagger = require("lovable-tagger");
  componentTagger = lovableTagger.componentTagger;
} catch (e) {
  console.warn("Warning: lovable-tagger not found, continuing without it");
  componentTagger = () => null; // Provide a no-op function
}

// Verify that react plugin is available
if (typeof react !== 'function') {
  console.error('ERROR: @vitejs/plugin-react-swc is not properly loaded!');
  console.error('This might cause build failures. Please check your installation.');
  // Don't throw here, try to continue with a fallback
}

export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 8000,
  },
  plugins: [
    // Only add react plugin if it's available
    typeof react === 'function' ? react() : null,
    mode === 'development' && componentTagger && componentTagger(),
  ].filter(Boolean), // Filter out null values
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
    outDir: 'dist',
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
