
const express = require('express');
const path = require('path');
const { createProxyMiddleware } = require('http-proxy-middleware');
const app = express();
const fs = require('fs');

// Log server startup information
console.log('---------- SERVER STARTUP INFO ----------');
console.log('Node version:', process.version);
console.log('Current directory:', __dirname);
console.log('Environment variables:', {
  NODE_ENV: process.env.NODE_ENV,
  PORT: process.env.PORT
});

// Check static directory
console.log('Static directory exists:', fs.existsSync(path.join(__dirname, 'static')));
if (fs.existsSync(path.join(__dirname, 'static'))) {
  console.log('Static directory contents:', fs.readdirSync(path.join(__dirname, 'static')));
  
  // Check for index.html specifically
  const indexPath = path.join(__dirname, 'static', 'index.html');
  console.log('index.html exists:', fs.existsSync(indexPath));
  if (fs.existsSync(indexPath)) {
    const stats = fs.statSync(indexPath);
    console.log('index.html size:', stats.size, 'bytes');
  }
}

// Serve static files from the static directory
app.use(express.static(path.join(__dirname, 'static')));
console.log('Configured static file serving from:', path.join(__dirname, 'static'));

// Proxy API requests to the FastAPI backend
app.use('/api', createProxyMiddleware({
  target: 'http://localhost:3000',
  changeOrigin: true,
  onProxyReq: (proxyReq, req) => {
    console.log('Proxying request:', req.method, req.url, 'to backend');
  },
  onError: (err, req, res) => {
    console.error('Proxy error:', err);
    res.status(500).send('Proxy error: Backend service unavailable');
  }
}));

// Add a health check endpoint
app.get('/health', (req, res) => {
  res.status(200).send({
    status: 'ok',
    timestamp: new Date().toISOString(),
    staticExists: fs.existsSync(path.join(__dirname, 'static')),
    env: process.env.NODE_ENV
  });
});

// For any request that doesn't match a static file, serve index.html
app.get('*', (req, res) => {
  console.log('Serving index.html for path:', req.path);
  const indexPath = path.join(__dirname, 'static', 'index.html');
  
  if (fs.existsSync(indexPath)) {
    res.sendFile(indexPath);
  } else {
    res.status(404).send('index.html not found. Available files: ' + 
      fs.existsSync(path.join(__dirname, 'static')) ? 
      fs.readdirSync(path.join(__dirname, 'static')).join(', ') : 
      'static directory not found');
  }
});

const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
  console.log('---------- SERVER STARTUP COMPLETE ----------');
});
