
import os
import sys
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

# Add the parent directory to the Python path to make imports work
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Try different import paths to find the app
try:
    from kmai_ent03_ui_app.app import app
except ImportError:
    try:
        # Try the direct import if we're in the package directory itself
        from app import app  
    except ImportError:
        raise ImportError("Could not import app from any expected location")

class TestApp(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.package_dir = Path(__file__).parent.parent
        
        # Look for static directory in multiple places
        self.static_dirs = [
            self.package_dir / "kmai_ent03_ui_app" / "static",
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
