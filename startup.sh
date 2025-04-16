
#!/bin/bash
set -e

echo "Starting deployment process..."

cd /home/site/wwwroot

# Check if Python is available and install Python dependencies first
if command -v python &> /dev/null || command -v python3 &> /dev/null; then
    echo "Python is available. Installing Python dependencies..."
    
    # Try to use pip or pip3, whichever is available
    if command -v pip &> /dev/null; then
        PIP_CMD="pip"
    elif command -v pip3 &> /dev/null; then
        PIP_CMD="pip3"
    else
        echo "ERROR: pip or pip3 is not available."
        exit 1
    fi
    
    # Install from setup.py
    $PIP_CMD install -e .
    
    # Also try requirements.txt as fallback
    if [ -f "requirements.txt" ]; then
        echo "Installing from requirements.txt as fallback..."
        $PIP_CMD install --no-cache-dir -r requirements.txt
    fi
fi

# Install Node.js dependencies if not already installed
if command -v npm &> /dev/null; then
    echo "Node.js is available. Installing Node.js dependencies..."
    if [ ! -d "node_modules" ]; then
        echo "Installing Node.js dependencies including dev dependencies..."
        npm ci
    fi
fi

# Build the static files if they don't exist
if [ ! -d "static" ]; then
    echo "Building static files..."
    npx vite build
fi

# Start the FastAPI server
echo "Starting FastAPI backend..."
cd /home/site/wwwroot
python -m uvicorn api.main:app --workers 2 --host 0.0.0.0 --port 3000 &

# Wait for backend to start
sleep 5
echo "Backend started"

# Start the Express server to serve static files and proxy API requests
echo "Starting Express server for frontend..."
cd /home/site/wwwroot
node server.js
