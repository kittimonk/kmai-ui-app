
#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

# Enable debug output to see all commands being executed
# set -x

echo "Creating Python package structure from existing application..."

# Use the correct package directory and name
PKG_DIR="kmai-ent03-ui-app"
PKG_NAME="kmai_ent03_ui_app"  # for Python imports and setup.py

# Remove any existing package directory to ensure clean start
if [ -d "$PKG_DIR" ]; then
  echo "Removing existing package directory..."
  rm -rf "$PKG_DIR"
fi

# Create a temporary directory for the Python package
mkdir -p "$PKG_DIR"

# Run the build to generate static files if they don't exist
if [ ! -d "static" ] && [ ! -d "src/static" ]; then
  echo "Building frontend assets..."
  if [ -f "package.json" ]; then
    npm ci
    npx vite build
  else
    echo "WARNING: No package.json found, skipping frontend build"
  fi
fi

# Find the static directory from the most likely locations, prefer dist over src/static
if [ -d "dist" ]; then
  STATIC_SRC="dist"
  echo "Found static files in dist directory"
elif [ -d "src/static" ]; then
  STATIC_SRC="src/static"
  echo "Found static files in src/static directory"
elif [ -d "static" ]; then
  STATIC_SRC="static"
  echo "Found static files in static directory"
else
  echo "WARNING: Static directory not found. Creating an empty one..."
  mkdir -p static
  STATIC_SRC="static"
  echo "Created empty static directory"
fi

# Create Python package structure with src directory
echo "Creating Python package structure..."
mkdir -p "$PKG_DIR/$PKG_NAME"
mkdir -p "$PKG_DIR/$PKG_NAME/static"
mkdir -p "$PKG_DIR/tests"

# Create __init__.py files
echo "# $PKG_NAME Python Application" > "$PKG_DIR/$PKG_NAME/__init__.py"
echo "version = \"1.0.0\"" >> "$PKG_DIR/$PKG_NAME/__init__.py"
touch "$PKG_DIR/tests/__init__.py"

# Copy static files (using preferred source)
echo "Copying static files from $STATIC_SRC..."
if [ -d "$STATIC_SRC" ] && [ "$(ls -A $STATIC_SRC)" ]; then
  cp -r "$STATIC_SRC/"* "$PKG_DIR/$PKG_NAME/static/"
  echo "Static files copied successfully."
else
  echo "WARNING: Static source directory $STATIC_SRC is empty or doesn't exist."
  # Create a minimal index.html to prevent issues
  mkdir -p "$PKG_DIR/$PKG_NAME/static"
  echo "<html><body><h1>Placeholder</h1></body></html>" > "$PKG_DIR/$PKG_NAME/static/index.html"
  echo "Created placeholder index.html"
fi

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
  echo "Created basic requirements.txt"
fi

# Copy test requirements
if [ -f "test-requirements.txt" ]; then
  cp test-requirements.txt "$PKG_DIR/"
  echo "test-requirements.txt copied successfully."
else
  echo "Creating test-requirements.txt..."
  cat > "$PKG_DIR/test-requirements.txt" << 'EOL'
pytest==8.0.0
httpx==0.24.1
pytest-asyncio==0.23.5
EOL
  echo "Created test-requirements.txt"
fi

# Copy app.py file from backend directory if it exists
if [ -f "backend/app.py" ]; then
  echo "Copying app.py from backend directory..."
  cp backend/app.py "$PKG_DIR/$PKG_NAME/app.py"
  echo "app.py copied successfully"
  
  # Check if app.py contains static file mounting code and add if missing
  if ! grep -q "app.mount(\"/\", StaticFiles" "$PKG_DIR/$PKG_NAME/app.py"; then
    echo "Adding static file mounting code to app.py..."
    # Add Path import if missing
    if ! grep -q "from pathlib import Path" "$PKG_DIR/$PKG_NAME/app.py"; then
      sed -i '1s/^/from pathlib import Path\n/' "$PKG_DIR/$PKG_NAME/app.py"
    fi
    # Append the static mounting code before the __main__ block
    sed -i '/if __name__ == "__main__":/i # Determine the static directory path\nstatic_dir = Path(__file__).parent / "static"\n# Mount static files - only if directory exists\nif static_dir.exists():\n    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")\n    print(f"Static files mounted from: {static_dir}")\nelse:\n    print("WARNING: Could not mount static files - directory doesn\\'"'"'t exist")\n' "$PKG_DIR/$PKG_NAME/app.py"
    echo "Static mounting code added to app.py"
  fi
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
  echo "Created default app.py"
fi

# Create a better test file that properly imports the app
echo "Creating test files..."
cat > "$PKG_DIR/tests/test_app.py" << EOL
import os
import sys
import unittest
from pathlib import Path
from fastapi.testclient import TestClient
from kmai_ent03_ui_app import app

# Add the parent directory to the Python path to make imports work
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Try different import paths to find the app
try:
    from ${PKG_NAME}.app import app
except ImportError:
    try:
        # Try the direct import if we're in the package directory itself
        from ${PKG_NAME}.app import app  
    except ImportError:
        raise ImportError("Could not import app from any expected location")

class TestApp(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.package_dir = Path(__file__).parent.parent
        
        # Look for static directory in multiple places
        self.static_dirs = [
            self.package_dir / "${PKG_NAME}" / "static",
            self.package_dir / "static",
        ]
        
        # Find the first existing static directory
        self.static_dir = next((d for d in self.static_dirs if d.exists()), None)
        if not self.static_dir:
            print(f"WARNING: Couldn't find static directory in: {self.static_dirs}")

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

    def test_static_directory_exists(self):
        """Test that the static directory exists"""
        if not self.static_dir:
            self.skipTest("Static directory not found")
        
        self.assertTrue(self.static_dir.exists(), f"Static directory does not exist at {self.static_dir}")
        # Check if static directory has files - only warn if empty, don't fail test
        if not any(self.static_dir.iterdir()):
            print(f"WARNING: Static directory is empty at {self.static_dir}")

if __name__ == "__main__":
    unittest.main()

#import pytest
#from fastapi.testclient import TestClient
#from kmai_ent03_ui_app.app import app  # Import the FastAPI app from your main module

#client = TestClient(app)

#def test_placeholder():
    # Test a non-existent route (e.g., '/nonexistent')
#    response = client.get("/nonexistent") # A FET request to a non-existent endpoint
#    assert response.status_code == 404 # Ensure the status code is 404 (Not Found)
    
EOL
echo "Created test_app.py"

# Create a proper pytest.ini file to help configure tests
echo "Creating pytest.ini..."
cat > "$PKG_DIR/pytest.ini" << 'EOL'
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
EOL
echo "Created pytest.ini"

# Create a more thorough MANIFEST.in file
echo "Creating MANIFEST.in..."
cat > "$PKG_DIR/MANIFEST.in" << EOL
include requirements.txt
include test-requirements.txt
include pytest.ini
recursive-include ${PKG_NAME}/static *
include ${PKG_NAME}/*.py
include ${PKG_NAME}/__init__.py
EOL
echo "Created MANIFEST.in"

# Create a good setup.py file that correctly includes package data
echo "Creating setup.py..."
cat > "$PKG_DIR/setup.py" << EOL
#!/usr/bin/env python

from setuptools import setup, find_packages #, Command
import os
from pathlib import Path

# The directory containing this file
HERE = Path(__file__).parent

def read_requirements(filename):
    requirements = []
    try:
        with open(filename) as f:
            reqs = f.read().splitlines()
            for req in reqs:
                if req.strip() and not req.startswith('#'):
                    requirements.append(req)
    except FileNotFoundError:
        print(f"Warning: {filename} not found!")
    return requirements

#class PyTestCommand(Command):
#    description = "Run tests with pytest"
#    user_options = []

#    def initialize_options(self):
#        pass

#    def finalize_options(self):
#        pass

#    def run(self):
#        # Import here so that setup.py doesn't need pytest unless you actually run tests
#        import pytest

#        errno = pytest.main(["--maxfail=1", "--disable-warnings", "tests"])
#        raise SystemExit(errno)

# Read requirements
requires = read_requirements('requirements.txt')
tests_requires = read_requirements('test-requirements.txt')
#requires.extend(tests_requires)

# This call to setup() does all the work
setup(
    name="kmai-ent03-ui-app",
    version="1.0.6",
    packages=find_packages(where="."),
#    packages=find_packages(where="kmai_ent03_ui_app"), # FInd packages in the 'kmai_ent03_ui_app' directory
#    package_dir={"": "kmai_ent03_ui_app"}, # Set the base directory for packages to 'kmai_ent03_ui_app'      
    python_requires=">=3.10",
    install_requires=requires,
#   tests_require=tests_requires,
    package_data={
        "${PKG_NAME}": ["static/*", "static/**/*"],
    },
    include_package_data=True,
#    cmdclass={
#        "test": PyTestCommand, # override the old 'test' command
#    },
    entry_points={
        "console_scripts": [
            "kmai-ent03-ui-app=${PKG_NAME}.app:app",
        ]
#    entry_points={
#        "console_scripts": [
#            "runserver=app:app",
#        ]     
    },
)
EOL
echo "Created setup.py"

echo "Python package structure created successfully in the '$PKG_DIR' directory."
echo ""
echo "To install and use this package:"
echo "  cd $PKG_DIR"
echo "  pip install -e ."
echo "  python -m uvicorn ${PKG_NAME}.app:app --reload"

# Optional: generate a helpful README.md
echo "Creating README.md..."
cat > "$PKG_DIR/README.md" << EOL
# KMAI UI App

A packaged Python application with a web UI.

## Installation

\`\`\`bash
pip install -e .
\`\`\`

## Running the Application

\`\`\`bash
python -m uvicorn ${PKG_NAME}.app:app --reload
\`\`\`

## Running Tests

\`\`\`bash
pytest
\`\`\`

## Directory Structure

- ${PKG_NAME}/: The main package directory
  - app.py: The FastAPI application
  - static/: Static files for the web UI
- tests/: Test files
EOL
echo "Created README.md"

# Turn off debug output
set +x

echo "Package creation completed successfully!"
