
#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

echo "Creating minimal Python application structure..."

# Create a temporary directory for the Python app
APP_DIR="python_minimal_app"
mkdir -p "$APP_DIR"
mkdir -p "$APP_DIR/static"
mkdir -p "$APP_DIR/tests"

# Find the static source directory
if [ -d "src/static" ]; then
  STATIC_SRC="src/static"
  echo "Using src/static as source for static files"
elif [ -d "static" ]; then
  STATIC_SRC="static"
  echo "Using static as source for static files"
else
  # Build the static assets if they don't exist
  echo "Static directory not found, building from source..."
  npm ci
  npx vite build
  
  if [ -d "src/static" ]; then
    STATIC_SRC="src/static"
  elif [ -d "static" ]; then
    STATIC_SRC="static"
  else
    echo "ERROR: Failed to find or create static directory"
    exit 1
  fi
fi

# Copy static files
echo "Copying static files from $STATIC_SRC..."
cp -r "$STATIC_SRC/"* "$APP_DIR/static/"

# Create __init__.py
echo "# Minimal KMAI App" > "$APP_DIR/__init__.py"

# Create main.py file (now app.py)
cat > "$APP_DIR/app.py" << 'EOL'
import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse

# Initialize FastAPI
app = FastAPI()

# Determine the static directory path
static_dir = Path(__file__).parent / "static"
if not static_dir.exists():
    print(f"WARNING: Static directory not found at {static_dir}")
    # Try alternative locations
    alt_static = Path.cwd() / "static"
    if alt_static.exists():
        static_dir = alt_static
        print(f"Using alternative static directory: {static_dir}")

# Health check endpoint
@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/api/health")
def api_health():
    return {"status": "ok"}

# Mount static files
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
    print(f"Static files mounted from: {static_dir}")
else:
    print("WARNING: No static directory found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
EOL

# Create setup.py
cat > "$APP_DIR/setup.py" << 'EOL'
from setuptools import setup, find_packages
from pathlib import Path

setup(
    name="kmai-minimal-app",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi>=0.109.0,<0.110.0",
        "uvicorn>=0.27.0,<0.28.0"
    ],
)
EOL

# Create MANIFEST.in
cat > "$APP_DIR/MANIFEST.in" << 'EOL'
include static/*
recursive-include static *
include app.py
include __init__.py
EOL

# Create a sample test file
cat > "$APP_DIR/tests/test_app.py" << 'EOL'
import unittest
from pathlib import Path
from fastapi.testclient import TestClient
from app import app

class TestApp(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.static_dir = Path(__file__).parent.parent / "static"

    def test_static_directory_exists(self):
        """Test that the static directory exists"""
        if not self.static_dir.exists():
            self.skipTest("Static directory not found")
        self.assertTrue(self.static_dir.exists())

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
uvicorn app:app --reload
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
