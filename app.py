
# Top level app.py for Azure App Service
import os
import sys

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the app from the actual module
from kmai_ent03_ui_app.app import app

# This will allow Azure to run this file directly
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("kmai_ent03_ui_app.app:app", host="0.0.0.0", port=port)
