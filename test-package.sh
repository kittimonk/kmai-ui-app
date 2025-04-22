
#!/bin/bash
set -e

# Install test requirements first
pip install -r test-requirements.txt

# Make the create-python-package.sh script executable
chmod +x create-python-package.sh

# Run the script
./create-python-package.sh

# Navigate to the generated package directory
cd python_package

# Verify that src/static directory exists and contains files
if [ ! -d "src/static" ]; then
  echo "ERROR: src/static directory does not exist"
  exit 1
fi

if [ -z "$(ls -A src/static)" ]; then
   echo "WARNING: src/static directory is empty. This may cause issues."
fi

# Install the package in development mode
pip install -e .

# Run the tests
python -m pytest tests/ -v

# Optional: Start the application to verify it works
# Uncomment these lines if you want the script to start the app
# cd src
# python -m uvicorn app:app --host 0.0.0.0 --port 8000
