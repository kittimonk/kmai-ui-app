
#!/bin/bash
set -e

# Install test requirements first
pip install -r test-requirements.txt

# Make the create-python-package.sh script executable
chmod +x create-python-package.sh

# Run the script
./create-python-package.sh

# Navigate to the generated package directory
cd kmai-ent03-ui-app

# Verify that the static directory exists and contains files
if [ ! -d "kmai_ent03_ui_app/static" ]; then
  echo "ERROR: kmai_ent03_ui_app/static directory does not exist"
  exit 1
fi

if [ -z "$(ls -A kmai_ent03_ui_app/static)" ]; then
   echo "WARNING: kmai_ent03_ui_app/static directory is empty. This may cause issues."
fi

# Install the package in development mode
pip install -e .

# Run the tests
python -m pytest tests/ -v

# Optional: Start the application to verify it works
# Uncomment these lines if you want the script to start the app
# python -m uvicorn kmai_ent03_ui_app.app:app --host 0.0.0.0 --port 8000

