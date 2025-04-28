
#!/bin/bash
set -e

echo "Starting test-package.sh script"

# Make sure setuptools and wheel are installed and up-to-date
echo "Installing setuptools and wheel..."
pip install --upgrade setuptools wheel

# Install test requirements first
echo "Installing test requirements..."
pip install -r test-requirements.txt

# Ensure node dependencies are installed, with extra checks for Vite plugins
echo "Installing Node.js dependencies..."
if [ -f "package.json" ]; then
  # First try normal installation
  npm ci
  
  # Explicitly check and install Vite plugin if missing
  echo "Checking for Vite plugin dependencies..."
  if [ ! -d "node_modules/@vitejs/plugin-react-swc" ]; then
    echo "Vite plugin missing, explicitly installing @vitejs/plugin-react-swc..."
    npm install --save-dev @vitejs/plugin-react-swc
  else
    echo "Vite plugin found in node_modules."
  fi
else
  echo "WARNING: No package.json found, skipping Node.js dependency installation"
fi

# Make the create-python-package.sh script executable
echo "Making create-python-package.sh executable..."
chmod +x create-python-package.sh

# Run the script
echo "Running create-python-package.sh..."
./create-python-package.sh

# Navigate to the generated package directory
echo "Navigating to the generated package directory..."
cd kmai-ent03-ui-app

# Verify that the static directory exists and contains files
echo "Checking for static directory..."
if [ ! -d "kmai_ent03_ui_app/static" ]; then
  echo "ERROR: kmai_ent03_ui_app/static directory does not exist"
  exit 1
fi

echo "Checking if static directory has files..."
if [ -z "$(ls -A kmai_ent03_ui_app/static)" ]; then
   echo "WARNING: kmai_ent03_ui_app/static directory is empty. This may cause issues."
fi

# Install the package in development mode to make imports work
echo "Installing the package in development mode..."
pip install -e .

# Add the current directory to PYTHONPATH to help with imports
echo "Setting PYTHONPATH..."
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Use either pytest or unittest, depending on what's installed
echo "Running tests..."
if command -v pytest &> /dev/null; then
  echo "Running tests with pytest..."
  python -m pytest tests/ -v
else
  echo "Running tests with unittest..."
  python -m unittest discover tests
fi

echo "Package tests completed successfully!"
