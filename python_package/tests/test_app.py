
import os
import unittest
from pathlib import Path
from kmai_ent03_ui_app.app import app

class TestApp(unittest.TestCase):
    def setUp(self):
        self.client = self._get_test_client()
        # Ensure we're in the right directory for tests
        self.package_dir = Path(__file__).parent.parent
        self.static_dir = self.package_dir / "src" / "static"

    def _get_test_client(self):
        try:
            from fastapi.testclient import TestClient
            return TestClient(app)
        except ImportError:
            raise RuntimeError("fastapi.testclient is required for tests")

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
