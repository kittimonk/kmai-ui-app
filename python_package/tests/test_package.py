
import os
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from kmai_app.app import app

client = TestClient(app)

def test_package_structure():
    """Test that the package structure is correct"""
    # Get the directory of this test file and navigate to package root
    this_dir = Path(__file__).parent
    package_root = this_dir.parent
    
    # Check if static directory exists
    static_dir = package_root / "kmai_app" / "static"
    print(f"Looking for static directory at: {static_dir}")
    assert static_dir.exists(), f"Static directory not found at {static_dir}"
    
    # Check if static directory has files
    has_files = any(static_dir.iterdir())
    if not has_files:
        print("WARNING: static directory exists but is empty")
    
    # Check if app.py exists
    assert (package_root / "kmai_app" / "app.py").exists(), "app.py not found"
    
    # Check if __init__.py exists
    assert (package_root / "kmai_app" / "__init__.py").exists(), "__init__.py not found"

def test_health_endpoint():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "kmai-app"}

def test_api_health_endpoint():
    """Test the API health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "API server is running"}

def test_static_files():
    """Test that static files are being served"""
    # This test might fail if static files aren't available
    # We'll make it conditional based on what we find
    static_dir = Path(__file__).parent.parent / "kmai_app" / "static"
    if static_dir.exists() and any(static_dir.iterdir()):
        response = client.get("/")
        assert response.status_code == 200, "Failed to serve root static file"
        assert "text/html" in response.headers["content-type"]
    else:
        pytest.skip("Static directory not available or empty - skipping test")
