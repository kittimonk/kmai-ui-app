
#!/bin/bash

# Build the Vite app to static directory
echo "Building Vite app to static directory..."
npm ci
npx vite build

# Ensure static directory exists
if [ -d "static" ]; then
  echo "Static folder successfully created."
else
  echo "ERROR: Static folder was not created. Build process may have failed."
  exit 1
fi

# Ensure backend is a proper Python package
mkdir -p backend
touch backend/__init__.py
echo '# This file makes the backend directory a proper Python package' > backend/__init__.py
echo 'version = "1.0.5"' >> backend/__init__.py

# Create MANIFEST.in file
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

# Create a setup.py file
echo "Creating setup.py file..."
cat > setup.py << 'EOL'
from setuptools import setup, find_packages

setup(
    name="kmai-ent03-ui-app",  # Match the package name in your .tar.gz
    version="1.0.5",  # Match the version in your .tar.gz
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

# Create startup.sh file
echo "Creating startup.sh file..."
cat > startup.sh << 'EOL'
#!/bin/bash
set -e

echo "Starting deployment process..."

cd /home/site/wwwroot

# Check if we already have a static folder
if [ ! -d "static" ]; then
    echo "Static folder not found. Building the app..."
    
    # Check if Node.js is available
    if command -v npm &> /dev/null; then
        echo "Installing Node.js dependencies..."
        npm ci
        
        echo "Building static files..."
        npx vite build
    else
        echo "WARNING: Node.js not available. Cannot build static files."
        # Assuming static files were included in the deployment package
    fi
fi

# Install Python dependencies
echo "Installing Python dependencies..."
if command -v pip &> /dev/null; then
    PIP_CMD="pip"
elif command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
else
    echo "ERROR: pip or pip3 is not available."
    exit 1
fi

echo "Installing Python dependencies from requirements.txt..."
$PIP_CMD install --no-cache-dir -r requirements.txt

# Install the package in development mode
echo "Installing the Python package in development mode..."
$PIP_CMD install -e .

# Start the FastAPI server
echo "Starting FastAPI backend..."
cd /home/site/wwwroot
python -m uvicorn backend.main:app --workers 2 --host 0.0.0.0 --port 3000 &

# Wait for backend to start
sleep 5
echo "Backend started"

# Start the Express server to serve static files and proxy API requests
echo "Starting Express server for frontend..."
cd /home/site/wwwroot
node server.js
EOL

# Explicitly create the egg-info directory with all required files
echo "Creating egg-info directory with required files..."
mkdir -p kmai_ent03_ui_app.egg-info
touch kmai_ent03_ui_app.egg-info/PKG-INFO
touch kmai_ent03_ui_app.egg-info/SOURCES.txt
touch kmai_ent03_ui_app.egg-info/dependency_links.txt
touch kmai_ent03_ui_app.egg-info/not-zip-safe
touch kmai_ent03_ui_app.egg-info/top_level.txt

# Create requires.txt with proper content
echo "Creating requires.txt with proper content..."
cat > kmai_ent03_ui_app.egg-info/requires.txt << 'EOL'
fastapi==0.109.0
uvicorn==0.27.0
python-jose==3.3.0
requests==2.31.0
python-multipart==0.0.6
sentence-transformers==2.2.2
scikit-learn==1.3.2
azure-storage-file-datalake==12.12.0
azure-storage-blob==12.18.0
azure-identity==1.14.0
azure-mgmt-cognitiveservices==13.5.0
openai==1.10.0
numpy==1.26.0
httpx==0.24.1
redis==5.0.1
pyodbc==5.0.1
striprtf==0.0.18
azure-search-documents==11.4.0
EOL

# Create top_level.txt with proper content
echo "Creating top_level.txt with proper content..."
echo "backend" > kmai_ent03_ui_app.egg-info/top_level.txt

# Install express and proxy middleware if not already installed
echo "Installing express and http-proxy-middleware..."
npm install express http-proxy-middleware --save

# List created files for verification
echo "Setup complete! The following files have been created or updated:"
ls -la
echo "Egg-info directory:"
ls -la kmai_ent03_ui_app.egg-info/
echo "Static directory:"
ls -la static/

echo "The application is ready for deployment to Azure App Service."
