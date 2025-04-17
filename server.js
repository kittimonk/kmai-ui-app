
const express = require('express');
const path = require('path');
const { createProxyMiddleware } = require('http-proxy-middleware');
const app = express();
const fs = require('fs');

// Log the current directory and check if static folder exists
console.log('Current directory:', __dirname);
console.log('Static directory exists:', fs.existsSync(path.join(__dirname, 'static')));
if (fs.existsSync(path.join(__dirname, 'static'))) {
  console.log('Static directory contents:', fs.readdirSync(path.join(__dirname, 'static')));
}

// Serve static files from the static directory
app.use(express.static(path.join(__dirname, 'static')));

// Proxy API requests to the FastAPI backend
app.use('/api', createProxyMiddleware({
  target: 'http://localhost:3000',
  changeOrigin: true
}));

// For any request that doesn't match a static file, serve index.html
app.get('*', (req, res) => {
  console.log('Serving index.html for path:', req.path);
  res.sendFile(path.join(__dirname, 'static', 'index.html'));
});

const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
