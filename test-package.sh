
#!/bin/bash
set -e

# Make the create-python-package.sh script executable
chmod +x create-python-package.sh

# Run the script
./create-python-package.sh

# Navigate to the generated package directory
cd python_package

# Install the package in development mode
pip install -e .

# Run the tests
python -m pytest tests/

# Start the application to verify it works
cd kmai_app
python -m uvicorn app:app --host 0.0.0.0 --port 3000

