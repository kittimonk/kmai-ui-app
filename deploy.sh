
#!/bin/bash

# Build the Vite app to static directory
echo "Building Vite app to static directory..."
npx vite build

# Create a Python package structure
echo "Creating Python package structure..."
if [ ! -f "setup.py" ]; then
    echo "Creating setup.py file..."
    cat > setup.py << 'EOL'
from setuptools import setup, find_packages

setup(
    name="ai-knowledge-app",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.109.0",
        "uvicorn==0.27.0",
        "python-jose==3.3.0",
        "requests==2.31.0",
        "python-multipart==0.0.6",
        "sentence-transformers==2.2.2",
        "scikit-learn==1.3.2",
        "azure-storage-file-datalake==12.12.0",
        "azure-storage-blob==12.18.0",
        "azure-identity==1.14.0",
        "azure-mgmt-cognitiveservices==13.5.0",
        "openai==1.10.0",
        "numpy==1.26.0",
        "httpx==0.24.1",
        "redis==5.0.1",
        "pyodbc==5.0.1",
        "striprtf==0.0.18",
        "azure-search-documents==11.4.0",
    ],
    include_package_data=True,
    zip_safe=False,
)
EOL
fi

# Create an empty __init__.py in the api folder to make it a proper Python package
mkdir -p api
touch api/__init__.py

# Create server.js file if it doesn't exist
echo "Creating server.js file..."
if [ ! -f "server.js" ]; then
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
fi

# Install express and proxy middleware if not already installed
echo "Installing express and http-proxy-middleware..."
npm install express http-proxy-middleware --save

echo "Setup complete! The application is ready for deployment to Azure App Service."
