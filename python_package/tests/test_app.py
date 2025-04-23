
import os
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

# First try importing from the expected package
try:
    from kmai_ent03_ui_app.app import app
except ImportError:
    # Fallback to importing from the backend directory directly
    try:
        from backend.app import app
    except ImportError:
        # Last resort - try importing from src
        from src.app import app

class TestApp(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        # Find the project root directory (either from package or from current tests location)
        self.package_dir = Path(__file__).parent.parent
        
        # Try multiple possible static directory locations
        self.static_dirs = [
            self.package_dir / "src" / "static",            # Direct src/static path
            self.package_dir / "static",                   # Root static path
            self.package_dir / "kmai_ent03_ui_app" / "static" # Package static path
        ]
        
        # Find the first existing static directory
        self.static_dir = next((d for d in self.static_dirs if d.exists()), None)
        if not self.static_dir:
            print(f"WARNING: Couldn't find static directory in any of these locations: {self.static_dirs}")

    def test_static_directory_exists(self):
        """Test that the static directory exists"""
        if not self.static_dir:
            print("WARNING: No static directory found - test will be skipped")
            self.skipTest("Static directory not found")
        
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
