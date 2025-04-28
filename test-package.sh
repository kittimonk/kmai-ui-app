
#!/bin/bash
set -e

echo "Starting test-package.sh script"

# Make sure setuptools and wheel are installed and up-to-date
echo "Installing setuptools and wheel..."
pip install --upgrade setuptools wheel

# Install test requirements first
echo "Installing test requirements..."
pip install -r test-requirements.txt

# Force clean installation of Node.js dependencies to resolve Vite plugin issues
echo "Force reinstalling Node.js dependencies..."
if [ -f "package.json" ]; then
  # Remove node_modules to ensure clean installation
  echo "Removing node_modules for clean installation..."
  rm -rf node_modules
  
  # Install dependencies with --legacy-peer-deps to avoid dependency conflicts
  echo "Installing dependencies with npm..."
  npm install --legacy-peer-deps
  
  # Explicitly install Vite plugin with multiple fallback methods
  echo "Explicitly installing Vite plugin..."
  if ! npm install --save-dev @vitejs/plugin-react-swc; then
    echo "Standard installation failed, trying with --no-save..."
    if ! npm install --no-save @vitejs/plugin-react-swc; then
      echo "Installation with --no-save failed, trying with --force..."
      if ! npm install --force --save-dev @vitejs/plugin-react-swc; then
        echo "ERROR: All attempts to install @vitejs/plugin-react-swc failed!"
        exit 1
      fi
    fi
  fi
  
  # Verify the installation
  if [ -d "node_modules/@vitejs/plugin-react-swc" ]; then
    echo "SUCCESS: @vitejs/plugin-react-swc has been installed and verified."
    ls -la node_modules/@vitejs/plugin-react-swc/
  else
    echo "ERROR: @vitejs/plugin-react-swc installation could not be verified!"
    exit 1
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
