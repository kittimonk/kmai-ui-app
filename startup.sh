
#!/bin/bash
set -e

echo "Starting deployment process..."

# Install Node.js dependencies if not already installed
if [ ! -d "node_modules" ]; then
  echo "Installing Node.js dependencies including dev dependencies..."
  npm ci
fi

# Install Python dependencies if not already installed
if [ ! -d "api/__pycache__" ]; then
  echo "Installing Python dependencies..."
  pip install --no-cache-dir -r requirements.txt
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
