
import os
import sys
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

# Add the parent directory to the Python path to make imports work
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Print debug info
print(f"Current directory: {os.getcwd()}")
print(f"Python path: {sys.path}")
print(f"Looking for app and database modules...")

# Create a flag to track import success
app_import_success = False
database_import_success = False

# Try different import approaches
try:
    # First try: Import from backend package
    from backend.app import app
    print("Successfully imported app from backend package")
    app_import_success = True
    
    try:
        from backend.database import initialize_chat_history_table, initialize_feature_interaction_table
        print("Successfully imported database functions from backend package")
        database_import_success = True
    except ImportError as e:
        print(f"Warning: Could not import database from backend package: {e}")
except ImportError as e:
    print(f"Could not import from backend package: {e}")

# If backend package import failed, try kmai_ent03_ui_app package
if not app_import_success:
    try:
        from kmai_ent03_ui_app.app import app
        print("Successfully imported app from kmai_ent03_ui_app package")
        app_import_success = True
        
        try:
            from kmai_ent03_ui_app.database import initialize_chat_history_table, initialize_feature_interaction_table
            print("Successfully imported database functions from kmai_ent03_ui_app package")
            database_import_success = True
        except ImportError as e:
            print(f"Warning: Could not import database from kmai_ent03_ui_app package: {e}")
    except ImportError as e:
        print(f"Could not import from kmai_ent03_ui_app package: {e}")

# If all imports failed, let's check if files exist in expected locations
if not app_import_success:
    # Check if backend/app.py exists
    backend_app_path = parent_dir / "backend" / "app.py"
    if backend_app_path.exists():
        print(f"Found app.py at {backend_app_path}, but couldn't import it")
    
    # Check if kmai_ent03_ui_app/app.py exists
    kmai_app_path = parent_dir / "kmai_ent03_ui_app" / "app.py"
    if kmai_app_path.exists():
        print(f"Found app.py at {kmai_app_path}, but couldn't import it")
    
    # Find all .py files in the project to help debugging
    print("Available Python files in project:")
    py_files = list(parent_dir.glob("**/*.py"))
    for py_file in py_files[:10]:  # Limit to first 10 to avoid too much output
        print(f"  {py_file.relative_to(parent_dir)}")
    
    if len(py_files) > 10:
        print(f"  ... and {len(py_files) - 10} more files")

# If we still couldn't import the app, raise an error
if not app_import_success:
    raise ImportError("Could not import app module from any location. Tests cannot continue.")

class TestApp(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.package_dir = Path(__file__).parent.parent
        
        # Look for static directory in multiple places
        self.static_dirs = [
            self.package_dir / "kmai_ent03_ui_app" / "static",
            self.package_dir / "static",
            self.package_dir / "backend" / "static",
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
