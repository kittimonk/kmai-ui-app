
import os
import pytest
from fastapi.testclient import TestClient
from kmai_app.app import app

client = TestClient(app)

def test_package_structure():
    """Test that the package structure is correct"""
    # Check if static directory exists
    assert os.path.exists(os.path.join("kmai_app", "static")), "Static directory not found"
    
    # Check if app.py exists
    assert os.path.exists(os.path.join("kmai_app", "app.py")), "app.py not found"
    
    # Check if __init__.py exists
    assert os.path.exists(os.path.join("kmai_app", "__init__.py")), "__init__.py not found"

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
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

