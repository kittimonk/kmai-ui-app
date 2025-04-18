#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

echo "Starting deployment process..."
echo "Current directory: $(pwd)"
echo "Listing all files in current directory:"
ls -la

cd /home/site/wwwroot
echo "Changed to wwwroot directory: $(pwd)"
echo "Listing all files in wwwroot:"
ls -la

# Check if we already have a static folder
if [ ! -d "static" ]; then
    echo "Static folder not found. Building the app..."
    
    # Check if Node.js is available
    if command -v npm &> /dev/null; then
        echo "Node.js version: $(node -v)"
        echo "NPM version: $(npm -v)"
        
        echo "Installing Node.js dependencies..."
        npm ci
        
        echo "Building static files..."
        npx vite build
        
        echo "Listing files after build:"
        ls -la
        
        if [ -d "static" ]; then
            echo "Static directory created successfully. Contents:"
            ls -la static/
        else
            echo "ERROR: Static directory was not created after build!"
        fi
    else
        echo "ERROR: Node.js not available. Cannot build static files."
        echo "Checking what files are available:"
        ls -la
        exit 1
    fi
fi

# Install Python dependencies
echo "Installing Python dependencies..."
if command -v pip &> /dev/null; then
    PIP_CMD="pip"
    echo "Using pip: $(pip --version)"
elif command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
    echo "Using pip3: $(pip3 --version)"
else
    echo "ERROR: pip or pip3 is not available."
    exit 1
fi

echo "Installing Python dependencies from requirements.txt..."
$PIP_CMD install --no-cache-dir -r requirements.txt

# Install the package in development mode
echo "Installing the Python package in development mode..."
$PIP_CMD install -e .

# Make sure Express.js server is installed
echo "Making sure Express.js dependencies are installed..."
npm install express http-proxy-middleware

# Start the FastAPI server with updated reference to app.py
echo "Starting FastAPI backend..."
cd /home/site/wwwroot
python -m uvicorn backend.app:app --workers 2 --host 0.0.0.0 --port 3000 &

# Wait for backend to start
sleep 5
echo "Backend started"

# Start the Express server to serve static files and proxy API requests
echo "Starting Express server for frontend..."
cd /home/site/wwwroot
node server.js
