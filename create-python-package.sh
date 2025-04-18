
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

# Create Python package structure
echo "Creating Python package structure..."
mkdir -p "$PACKAGE_DIR/kmai_app"
mkdir -p "$PACKAGE_DIR/kmai_app/static"
mkdir -p "$PACKAGE_DIR/tests"

# Create __init__.py files
echo "# KMAI Python Application" > "$PACKAGE_DIR/kmai_app/__init__.py"
echo "version = \"1.0.0\"" >> "$PACKAGE_DIR/kmai_app/__init__.py"

# Copy static files
echo "Copying static files..."
cp -r static/* "$PACKAGE_DIR/kmai_app/static/"

# Create main.py file
cat > "$PACKAGE_DIR/kmai_app/main.py" << 'EOL'
import os
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

# Health check endpoint
@app.get("/health")
def health():
    return {"status": "healthy", "service": "kmai-app"}

@app.get("/api/health")
def api_health():
    return {"status": "ok", "message": "API server is running"}

# Copy relevant API endpoints from original main.py
# ... Add your API endpoints here

# Mount static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# Fallback route for SPA
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    return FileResponse("static/index.html")

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

# Create a sample test file
cat > "$PACKAGE_DIR/tests/test_app.py" << 'EOL'
import unittest
from fastapi.testclient import TestClient
from kmai_app.main import app

class TestApp(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

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

# Create a README.md file
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
python main.py
```

Or using uvicorn directly:

```bash
uvicorn kmai_app.main:app --reload
```

## Running Tests

```bash
python -m unittest discover
```
EOL

echo "Python package structure created in the '$PACKAGE_DIR' directory."
echo "To create a new repository with these files:"
echo "1. Create a new Git repository"
echo "2. Copy the contents of the '$PACKAGE_DIR' directory into it"
echo "3. Commit and push the files"
echo ""
echo "Done!"
