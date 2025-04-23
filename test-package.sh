
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

# Install the package in development mode to make imports work
pip install -e .

# Add the current directory to PYTHONPATH to help with imports
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Use either pytest or unittest, depending on what's installed
if command -v pytest &> /dev/null; then
  echo "Running tests with pytest..."
  python -m pytest tests/ -v
else
  echo "Running tests with unittest..."
  python -m unittest discover tests
fi

echo "Package tests completed successfully!"
