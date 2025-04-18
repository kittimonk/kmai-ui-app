
#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

echo "Creating minimal Python application structure..."

# Create a temporary directory for the Python app
APP_DIR="python_minimal_app"
mkdir -p "$APP_DIR"
mkdir -p "$APP_DIR/static"
mkdir -p "$APP_DIR/tests"

# Build the static assets if they don't exist
if [ ! -d "static" ] || [ -z "$(ls -A static 2>/dev/null)" ]; then
  echo "Building static files..."
  npm ci
  npx vite build
fi

# Copy static files
echo "Copying static files..."
cp -r static/* "$APP_DIR/static/"

# Create __init__.py
echo "# Minimal KMAI App" > "$APP_DIR/__init__.py"

# Create main.py file
cat > "$APP_DIR/main.py" << 'EOL'
import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse

# Initialize FastAPI
app = FastAPI()

# Health check endpoint
@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/api/health")
def api_health():
    return {"status": "ok"}

# Mount static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
EOL

# Create setup.py
cat > "$APP_DIR/setup.py" << 'EOL'
from setuptools import setup

setup(
    name="kmai-minimal-app",
    version="1.0.0",
    py_modules=["main"],
    install_requires=[
        "fastapi==0.109.0",
        "uvicorn==0.27.0"
    ],
)
EOL

# Create MANIFEST.in
cat > "$APP_DIR/MANIFEST.in" << 'EOL'
include static/*
recursive-include static *
include main.py
include __init__.py
EOL

# Create a sample test file
cat > "$APP_DIR/tests/test_app.py" << 'EOL'
import unittest
from fastapi.testclient import TestClient
from main import app

class TestApp(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "healthy"})

if __name__ == "__main__":
    unittest.main()
EOL

# Create README with instructions
cat > "$APP_DIR/README.md" << 'EOL'
# Minimal KMAI Python App

A minimal Python application structure containing just:
- Pre-built static frontend files
- A simple FastAPI backend
- Basic project structure for Python packaging

## Running the Application

```bash
uvicorn main:app --reload
```

## Deploying as a Python Package

This application is structured as a Python package that can be installed with pip:

```bash
pip install -e .
```
EOL

echo "Minimal Python application structure created in the '$APP_DIR' directory."
echo "To use this as a separate repository:"
echo "1. Create a new Git repository"
echo "2. Copy the contents of the '$APP_DIR' directory into it"
echo "3. Commit and push the files"
echo ""
echo "Done!"
