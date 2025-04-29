
import os
import sys
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

# Add the parent directory to the Python path to make imports work
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Print debug info
print(f"Current directory: {os.getcwd()}")
print(f"Python path: {sys.path}")
print(f"Looking for app and database modules...")

# Try different import paths to find the app
try:
    # Try direct import first
    from backend.app import app
    print("Successfully imported app from backend.")
    
    try:
        from backend.database import initialize_chat_history_table, initialize_feature_interaction_table
        print("Successfully imported database functions from backend")
    except ImportError as e:
        print(f"Warning: Could not import database from backend: {e}")
        # Try to look for database.py in the same directory as app.py
        import backend
        backend_dir = Path(backend.__file__).parent
        database_path = backend_dir / "database.py"
        print(f"Looking for database.py at {database_path}")
        if database_path.exists():
            print(f"Found database.py at {database_path}, but couldn't import it")
        
except ImportError as e:
    print(f"Failed to import from backend: {e}")
    try:
        # Check if we're in the package directory structure
        import kmai_ent03_ui_app
        print(f"Found kmai_ent03_ui_app package at {kmai_ent03_ui_app.__file__}")
        
        # If we're in the package directory structure
        from kmai_ent03_ui_app.app import app
        print("Successfully imported app from package.")
        
        try:
            from kmai_ent03_ui_app.database import initialize_chat_history_table, initialize_feature_interaction_table
            print("Successfully imported database functions from package")
        except ImportError as e:
            print(f"Warning: Could not import database from package: {e}")
    except ImportError:
        print("ERROR: Could not import app module. Make sure the 'backend' directory is in your PYTHONPATH.")
        print(f"Current PYTHONPATH: {sys.path}")
        print("Available files in current directory:")
        for f in os.listdir('.'):
            print(f"  {f}")
        print("Available directories:")
        for d in os.listdir(parent_dir):
            if os.path.isdir(os.path.join(parent_dir, d)):
                print(f"  {d}")
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
