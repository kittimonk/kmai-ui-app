
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
echo '# This file makes the backend directory a proper Python package' > backend/__init__.py
echo 'version = "1.0.5"' >> backend/__init__.py

# Create MANIFEST.in if it doesn't exist
echo "Creating MANIFEST.in file..."
cat > MANIFEST.in << 'EOL'
include requirements.txt
include backend/requirements.txt
include static/*
recursive-include static *
recursive-include backend *
include setup.py
EOL

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

# Create a setup.py file that explicitly creates the egg-info folder
echo "Creating setup.py file..."
cat > setup.py << 'EOL'
from setuptools import setup, find_packages

setup(
    name="kmai-ent03-ui-app",
    version="1.0.5",
    packages=find_packages(),
    include_package_data=True,
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
    python_requires=">=3.8",
    zip_safe=False,
)
EOL

# Explicitly create the egg-info directory and requires.txt
mkdir -p kmai_ent03_ui_app.egg-info
touch kmai_ent03_ui_app.egg-info/requires.txt
echo "fastapi==0.109.0" > kmai_ent03_ui_app.egg-info/requires.txt

# Install express and proxy middleware if not already installed
echo "Installing express and http-proxy-middleware..."
npm install express http-proxy-middleware --save

echo "Setup complete! The application is ready for deployment to Azure App Service."
