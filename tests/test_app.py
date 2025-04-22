
import os
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

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
    static_dir = Path(__file__).parent.parent / "src" / "static"
    if static_dir.exists() and any(static_dir.iterdir()):
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    else:
        pytest.skip("Static directory not available or empty - skipping test")
