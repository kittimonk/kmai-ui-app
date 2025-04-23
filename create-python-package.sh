
#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

echo "Creating Python package structure from existing application..."

# Use the correct package directory and name
PKG_DIR="kmai-ent03-ui-app"
PKG_NAME="kmai_ent03_ui_app"  # for Python imports and setup.py

# Create a temporary directory for the Python package
mkdir -p "$PKG_DIR"

# Run the build to generate static files
echo "Building frontend assets..."
npm ci
npx vite build

# Find the static directory from the most likely locations, prefer src/static
if [ -d "src/static" ]; then
  STATIC_SRC="src/static"
elif [ -d "static" ]; then
  STATIC_SRC="static"
else
  echo "ERROR: Static directory not found in either src/static or static."
  exit 1
fi

# Create Python package structure with src directory
echo "Creating Python package structure..."
mkdir -p "$PKG_DIR/$PKG_NAME"
mkdir -p "$PKG_DIR/$PKG_NAME/static"
mkdir -p "$PKG_DIR/tests"

# Create __init__.py files
echo "# $PKG_NAME Python Application" > "$PKG_DIR/$PKG_NAME/__init__.py"
echo "version = \"1.0.0\"" >> "$PKG_DIR/$PKG_NAME/__init__.py"

# Copy static files (using preferred source)
echo "Copying static files from $STATIC_SRC..."
cp -r "$STATIC_SRC/"* "$PKG_DIR/$PKG_NAME/static/"
echo "Static files copied successfully."

# Copy requirements.txt to package directory
echo "Copying requirements.txt to package directory..."
if [ -f "requirements.txt" ]; then
  cp requirements.txt "$PKG_DIR/"
  echo "requirements.txt copied successfully."
else
  echo "Warning: requirements.txt not found. Creating a basic one."
  cat > "$PKG_DIR/requirements.txt" << 'EOL'
fastapi>=0.109.0,<0.110.0
uvicorn>=0.27.0,<0.28.0
python-jose>=3.3.0,<3.4.0
requests>=2.31.0,<2.32.0
python-multipart>=0.0.6,<0.1.0
EOL
fi

# Copy app.py file from backend directory if it exists
if [ -f "backend/app.py" ]; then
  echo "Copying app.py from backend directory..."
  mkdir -p "$PKG_DIR/$PKG_NAME"
  cp backend/app.py "$PKG_DIR/$PKG_NAME/app.py"
  
  # Check if app.py contains static file mounting code
  if ! grep -q "app.mount(\"/\", StaticFiles" "$PKG_DIR/$PKG_NAME/app.py"; then
    echo "Adding static file mounting code to app.py..."
    # Add Path import if missing
    if ! grep -q "from pathlib import Path" "$PKG_DIR/$PKG_NAME/app.py"; then
      sed -i '1s/^/from pathlib import Path\n/' "$PKG_DIR/$PKG_NAME/app.py"
    fi
    # Append the static mounting code before the __main__ block
    sed -i '/if __name__ == "__main__":/i # Determine the static directory path\nstatic_dir = Path(__file__).parent / "static"\n# Mount static files - only if directory exists\nif static_dir.exists():\n    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")\n    print(f"Static files mounted from: {static_dir}")\nelse:\n    print("WARNING: Could not mount static files - directory doesn\\'"'"'t exist")\n' "$PKG_DIR/$PKG_NAME/app.py"
  fi
  
  # Make sure the port is 8000 in the __main__ block
  sed -i 's/port=int(os.environ.get("PORT", [0-9]\+))/port=int(os.environ.get("PORT", 8000))/g' "$PKG_DIR/$PKG_NAME/app.py"
  
  echo "app.py copied and updated successfully from backend directory."
else
  # Create app.py file in package directory
  echo "Creating default app.py in package directory..."
  cat > "$PKG_DIR/$PKG_NAME/app.py" << 'EOL'
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

# Create a better test file that properly imports the app using the correct package name
cat > "$PKG_DIR/tests/test_app.py" << EOL
import os
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

# Try to import the app from the package
try:
    from $PKG_NAME.app import app
except ImportError:
    # If that fails, try a direct import (useful during development)
    from app import app

class TestApp(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        # Find the project root directory
        self.package_dir = Path(__file__).parent.parent
        self.static_dir = self.package_dir / "$PKG_NAME" / "static"

    def test_static_directory_exists(self):
        """Test that the static directory exists"""
        print(f"Checking static directory at: {self.static_dir}")
        self.assertTrue(self.static_dir.exists(), f"Static directory does not exist at {self.static_dir}")
        # Check if static directory has files
        self.assertTrue(any(self.static_dir.iterdir()), f"Static directory is empty at {self.static_dir}")

    def test_health_endpoint(self):
        """Test the health check endpoint"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "healthy", "service": "kmai-app"})

    def test_api_health_endpoint(self):
        """Test the API health check endpoint"""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "message": "API server is running"})

if __name__ == "__main__":
    unittest.main()
EOL

# Create a proper pytest.ini file to help configure tests
cat > "$PKG_DIR/pytest.ini" << 'EOL'
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
EOL

# Create __init__.py in tests directory to make it a proper package
touch "$PKG_DIR/tests/__init__.py"

# Update test-requirements.txt
cat > "$PKG_DIR/test-requirements.txt" << 'EOL'
pytest==8.0.0
httpx==0.24.1
pytest-asyncio==0.23.5
EOL

# Create a more thorough MANIFEST.in file
cat > "$PKG_DIR/MANIFEST.in" << EOL
include requirements.txt
include test-requirements.txt
include pytest.ini
recursive-include $PKG_NAME/static *
include $PKG_NAME/*.py
include $PKG_NAME/__init__.py
EOL

echo "Python package structure created successfully in the '$PKG_DIR' directory."
echo "To install and use this package:"
echo "  cd $PKG_DIR"
echo "  pip install -e ."
echo "  python -m uvicorn $PKG_NAME.app:app --reload"
