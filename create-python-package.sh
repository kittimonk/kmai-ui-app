
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

# Create Python package structure
echo "Creating Python package structure..."
mkdir -p "$PACKAGE_DIR/kmai_app"
mkdir -p "$PACKAGE_DIR/kmai_app/static"
mkdir -p "$PACKAGE_DIR/tests"

# Create __init__.py files
echo "# KMAI Python Application" > "$PACKAGE_DIR/kmai_app/__init__.py"
echo "version = \"1.0.0\"" >> "$PACKAGE_DIR/kmai_app/__init__.py"

# Copy static files - ensure the static directory exists in destination first
echo "Copying static files..."
if [ -d "static" ]; then
  # Make sure the destination directory exists
  mkdir -p "$PACKAGE_DIR/kmai_app/static"
  cp -r static/* "$PACKAGE_DIR/kmai_app/static/"
  echo "Static files copied successfully."
else
  echo "Warning: static directory not found. This may cause issues."
fi

# Create app.py file
cat > "$PACKAGE_DIR/kmai_app/app.py" << 'EOL'
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

# Copy relevant API endpoints from original main.py
# ... Add your API endpoints here

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

# Create setup.py
cat > "$PACKAGE_DIR/setup.py" << 'EOL'
from setuptools import setup, find_packages

setup(
    name="kmai-app",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi==0.109.0",
        "uvicorn==0.27.0",
        "python-jose==3.3.0",
        "requests==2.31.0",
        "python-multipart==0.0.6"
    ],
    python_requires=">=3.8",
    zip_safe=False,
)
EOL

# Create MANIFEST.in
cat > "$PACKAGE_DIR/MANIFEST.in" << 'EOL'
include requirements.txt
recursive-include kmai_app/static *
include kmai_app/*.py
EOL

# Create requirements.txt
cat > "$PACKAGE_DIR/requirements.txt" << 'EOL'
fastapi==0.109.0
uvicorn==0.27.0
python-jose==3.3.0
requests==2.31.0
python-multipart==0.0.6
EOL

# Create a modified test file that checks for static directory existence
cat > "$PACKAGE_DIR/tests/test_app.py" << 'EOL'
import os
import unittest
from pathlib import Path
from fastapi.testclient import TestClient
from kmai_app.app import app

class TestApp(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        # Ensure we're in the right directory for tests
        self.package_dir = Path(__file__).parent.parent
        self.static_dir = self.package_dir / "kmai_app" / "static"
        
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

# Create a helpful README.md file
cat > "$PACKAGE_DIR/README.md" << 'EOL'
# KMAI Python Application

This is a Python package containing the KMAI application with a FastAPI backend and pre-built static frontend assets.

## Installation

```bash
pip install -e .
```

## Running the Application

```bash
cd kmai_app
python app.py
```

Or using uvicorn directly:

```bash
uvicorn kmai_app.app:app --reload
```

## Running Tests

```bash
python -m unittest discover
```

## Troubleshooting

### Static directory missing
If you encounter errors about the static directory not existing:

1. Make sure you run the build process first: `npm ci && npx vite build`
2. Check that the `static` directory exists and contains the built files
3. Ensure the files are properly copied to `kmai_app/static/` during package creation
EOL

echo "Python package structure created in the '$PACKAGE_DIR' directory."
echo "To create a new repository with these files:"
echo "1. Create a new Git repository"
echo "2. Copy the contents of the '$PACKAGE_DIR' directory into it"
echo "3. Commit and push the files"
echo ""
echo "Done!"
