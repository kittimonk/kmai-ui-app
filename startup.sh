
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

# Start the FastAPI server - updated path to correct module
echo "Starting FastAPI backend..."
cd /home/site/wwwroot
export PYTHONPATH="/home/site/wwwroot:${PYTHONPATH}"
python -m uvicorn kmai_ent03_ui_app.app:app --host 0.0.0.0 --port $PORT
