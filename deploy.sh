
#!/bin/bash

# Build the Vite app to static directory
echo "Building Vite app to static directory..."
npm ci
npx vite build

# Create a Python package structure
echo "Creating Python package structure..."

# Ensure backend is a proper Python package
mkdir -p backend
touch backend/__init__.py

# Create MANIFEST.in if it doesn't exist
if [ ! -f "MANIFEST.in" ]; then
    echo "Creating MANIFEST.in file..."
    cat > MANIFEST.in << 'EOL'
include requirements.txt
include backend/requirements.txt
include static/*
recursive-include static *
EOL
fi

# Create/update server.js file
echo "Creating server.js file..."
cat > server.js << 'EOL'
const express = require('express');
const path = require('path');
const { createProxyMiddleware } = require('http-proxy-middleware');
const app = express();

// Serve static files from the static directory
app.use(express.static(path.join(__dirname, 'static')));

// Proxy API requests to the FastAPI backend
app.use('/api', createProxyMiddleware({
  target: 'http://localhost:3000',
  changeOrigin: true
}));

// For any request that doesn't match a static file, serve index.html
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'static', 'index.html'));
});

const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
EOL

# Install express and proxy middleware if not already installed
echo "Installing express and http-proxy-middleware..."
npm install express http-proxy-middleware --save

echo "Setup complete! The application is ready for deployment to Azure App Service."
