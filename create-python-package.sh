
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

# Copy requirements.txt to package directory
echo "Copying requirements.txt to package directory..."
cp requirements.txt "$PACKAGE_DIR/"

# Copy app.py file from backend directory if it exists
if [ -f "backend/app.py" ]; then
  echo "Copying app.py from backend directory..."
  cp backend/app.py "$PACKAGE_DIR/src/app.py"
  
  # Check if app.py contains static file mounting code
  if ! grep -q "app.mount(\"/\", StaticFiles" "$PACKAGE_DIR/src/app.py"; then
    echo "Adding static file mounting code to app.py..."
    # Append the static mounting code before the __main__ block
    sed -i '/if __name__ == "__main__":/i # Determine the static directory path\nstatic_dir = Path(__file__).parent / "static"\n# Mount static files - only if directory exists\nif static_dir.exists():\n    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")\n    print(f"Static files mounted from: {static_dir}")\nelse:\n    print("WARNING: Could not mount static files - directory doesn\\'"'"'t exist")\n' "$PACKAGE_DIR/src/app.py"
  fi
  
  # Make sure the port is 8000 in the __main__ block
  sed -i 's/port=int(os.environ.get("PORT", [0-9]\+))/port=int(os.environ.get("PORT", 8000))/g' "$PACKAGE_DIR/src/app.py"
  
  echo "app.py copied and updated successfully from backend directory."
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
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
EOL
fi

# Update setup.py with read_requirements function that handles file not found scenario
cat > "$PACKAGE_DIR/setup.py" << 'EOL'
from setuptools import setup, find_packages
import os

def read_requirements():
    try:
        with open('requirements.txt', 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        # Fallback to basic dependencies if requirements.txt is not found
        print("WARNING: requirements.txt not found, using default dependencies")
        return [
            "fastapi>=0.109.0,<0.110.0",
            "uvicorn>=0.27.0,<0.28.0",
            "python-jose>=3.3.0,<3.4.0",
            "requests>=2.31.0,<2.32.0",
            "python-multipart>=0.0.6,<0.1.0"
        ]

setup(
    name="kmai-app",
    version="1.0.0",
    packages=find_packages(),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=read_requirements(),
    python_requires=">=3.11",
    zip_safe=False,
)
EOL

# Update MANIFEST.in for new structure and to include requirements.txt
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

echo "Python package structure created successfully in the '$PACKAGE_DIR' directory."
