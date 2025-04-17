
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
