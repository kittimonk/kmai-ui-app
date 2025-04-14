
#!/bin/bash

# Install Vite globally if not already installed
echo "Checking for Vite..."
if ! command -v vite &> /dev/null; then
    echo "Installing Vite globally..."
    npm install -g vite
fi

# Build the Vite app to static directory
echo "Building Vite app to static directory..."
npx vite build

# Create a simple server to serve the app on port 3000
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
  changeOrigin: true,
  pathRewrite: {
    '^/api': '' // Remove /api prefix when forwarding to the backend
  }
}));

// For any request that doesn't match a static file, serve index.html
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'static', 'index.html'));
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
EOL

# Install express and proxy middleware if not already installed
echo "Installing express and http-proxy-middleware..."
npm install express http-proxy-middleware --save

echo "Setup complete!"
echo "Run 'node server.js' to start the server on port 3000"
