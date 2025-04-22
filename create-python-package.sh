
#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

echo "Creating Python package structure from existing application..."

# Create a temporary directory for the Python package
PACKAGE_DIR="python_package"
mkdir -p "$PACKAGE_DIR"

# Run the build to generate static files
echo "Building frontend assets..."
npm ci
npx vite build

# Verify the build output
if [ ! -d "static" ]; then
  echo "ERROR: Static directory was not created by the build process."
  exit 1
fi

# Create Python package structure with src directory
echo "Creating Python package structure..."
mkdir -p "$PACKAGE_DIR/src"
mkdir -p "$PACKAGE_DIR/src/static"
mkdir -p "$PACKAGE_DIR/tests"

# Create __init__.py files
echo "# KMAI Python Application" > "$PACKAGE_DIR/src/__init__.py"
echo "version = \"1.0.0\"" >> "$PACKAGE_DIR/src/__init__.py"

# Copy static files
echo "Copying static files..."
if [ -d "static" ]; then
  # Make sure the destination directory exists
  mkdir -p "$PACKAGE_DIR/src/static"
  cp -r static/* "$PACKAGE_DIR/src/static/"
  echo "Static files copied successfully."
else
  echo "Warning: static directory not found. This may cause issues."
fi

# Copy app.py file from backend directory if it exists
if [ -f "backend/app.py" ]; then
  echo "Copying app.py from backend directory..."
  cp backend/app.py "$PACKAGE_DIR/src/app.py"
  echo "app.py copied successfully from backend directory."
else
  # Create app.py file in src directory
  echo "Creating default app.py in src directory..."
  cat > "$PACKAGE_DIR/src/app.py" << 'EOL'
import os
import sys
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse

# Initialize FastAPI
app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:3000",
    "http://localhost:8080",
    os.environ.get("WEBSITE_HOSTNAME", "*")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Determine the static directory path
static_dir = Path(__file__).parent / "static"
if not static_dir.exists():
    print(f"WARNING: Static directory not found at {static_dir}")
    # Try alternative locations
    alt_static = Path.cwd() / "static"
    if alt_static.exists():
        static_dir = alt_static
        print(f"Using alternative static directory: {static_dir}")
    else:
        print("ERROR: Could not find static directory")
        # Create an empty directory to prevent crashes
        static_dir.mkdir(exist_ok=True)

# Health check endpoint
@app.get("/health")
def health():
    return {"status": "healthy", "service": "kmai-app"}

@app.get("/api/health")
def api_health():
    return {"status": "ok", "message": "API server is running"}

# Mount static files - only if directory exists
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
    print(f"Static files mounted from: {static_dir}")
else:
    print("WARNING: Could not mount static files - directory doesn't exist")

# Fallback route for SPA
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    index_html = static_dir / "index.html"
    if index_html.exists():
        return FileResponse(str(index_html))
    else:
        return JSONResponse(
            status_code=404,
            content={"error": "Static files not found. Please build the frontend."}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
EOL
fi

# Update setup.py to reflect new structure and Python version requirement
cat > "$PACKAGE_DIR/setup.py" << 'EOL'
from setuptools import setup, find_packages

setup(
    name="kmai-app",
    version="1.0.0",
    packages=find_packages(),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "fastapi==0.109.0",
        "uvicorn==0.27.0",
        "python-jose==3.3.0",
        "requests==2.31.0",
        "python-multipart==0.0.6"
    ],
    python_requires=">=3.11",
    zip_safe=False,
)
EOL

# Update MANIFEST.in for new structure
cat > "$PACKAGE_DIR/MANIFEST.in" << 'EOL'
include requirements.txt
recursive-include src/static *
include src/*.py
EOL

# Create test file with updated imports
cat > "$PACKAGE_DIR/tests/test_app.py" << 'EOL'
import os
import unittest
from pathlib import Path
from fastapi.testclient import TestClient
from src.app import app

class TestApp(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        # Ensure we're in the right directory for tests
        self.package_dir = Path(__file__).parent.parent
        self.static_dir = self.package_dir / "src" / "static"
        
    def test_static_directory_exists(self):
        """Test that the static directory exists"""
        print(f"Checking static directory at: {self.static_dir}")
        self.assertTrue(self.static_dir.exists(), f"Static directory does not exist at {self.static_dir}")
        
    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "healthy", "service": "kmai-app"})

    def test_api_health_endpoint(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "message": "API server is running"})

if __name__ == "__main__":
    unittest.main()
EOL
