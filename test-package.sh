
#!/bin/bash
set -e

echo "Starting test-package.sh script"

# Make sure setuptools and wheel are installed and up-to-date
echo "Installing setuptools and wheel..."
pip install --upgrade setuptools wheel

# Install test requirements first
echo "Installing test requirements..."
pip install -r test-requirements.txt

# Check if Vite plugin is already installed
PLUGIN_INSTALLED=false
if [ -d "node_modules/@vitejs/plugin-react-swc" ]; then
  echo "Vite plugin found before dependency installation"
  PLUGIN_INSTALLED=true
  # Backup the plugin directory
  echo "Backing up existing plugin..."
  mkdir -p .temp_backup
  cp -r node_modules/@vitejs/plugin-react-swc .temp_backup/
fi

# Force clean installation of Node.js dependencies to resolve Vite plugin issues
echo "Installing Node.js dependencies..."
if [ -f "package.json" ]; then
  # Install dependencies with --legacy-peer-deps to avoid dependency conflicts
  # But don't remove node_modules completely to preserve our plugin if it's already there
  echo "Installing dependencies with npm..."
  npm install --legacy-peer-deps
  
  # Check if plugin was preserved or needs to be reinstalled
  if [ ! -d "node_modules/@vitejs/plugin-react-swc" ]; then
    echo "Plugin not found after npm install"
    
    # Restore from backup if we had it
    if [ "$PLUGIN_INSTALLED" = true ] && [ -d ".temp_backup/plugin-react-swc" ]; then
      echo "Restoring plugin from backup..."
      mkdir -p node_modules/@vitejs/
      cp -r .temp_backup/plugin-react-swc node_modules/@vitejs/
    else
      # Explicitly install Vite plugin with multiple fallback methods
      echo "Explicitly installing Vite plugin..."
      npm install --save-dev @vitejs/plugin-react-swc || true
      
      if [ ! -d "node_modules/@vitejs/plugin-react-swc" ]; then
        echo "Standard installation failed, trying with --no-save..."
        npm install --no-save @vitejs/plugin-react-swc || true
      fi
      
      if [ ! -d "node_modules/@vitejs/plugin-react-swc" ]; then
        echo "Installation with --no-save failed, trying with --force..."
        npm install --force --save-dev @vitejs/plugin-react-swc || true
      fi
    fi
  fi
  
  # Verify the installation
  if [ -d "node_modules/@vitejs/plugin-react-swc" ]; then
    echo "SUCCESS: @vitejs/plugin-react-swc has been installed and verified."
    ls -la node_modules/@vitejs/plugin-react-swc/
  else
    echo "ERROR: @vitejs/plugin-react-swc installation could not be verified!"
    echo "This may cause the build to fail. Continuing anyway..."
  fi
else
  echo "WARNING: No package.json found, skipping Node.js dependency installation"
fi

# Clean up backup
if [ -d ".temp_backup" ]; then
  rm -rf .temp_backup
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

# Debug: Check if database.py was copied properly
echo "Checking for database.py..."
if [ -f "kmai_ent03_ui_app/database.py" ]; then
  echo "SUCCESS: database.py found in the package"
else
  echo "ERROR: database.py not found in kmai_ent03_ui_app/"
  # Check if it exists in the parent directory
  if [ -f "../backend/database.py" ]; then
    echo "Found database.py in ../backend/ - copying it now"
    cp "../backend/database.py" "kmai_ent03_ui_app/"
  else
    echo "Could not find database.py in any expected location"
  fi
fi

# Install the package in development mode to make imports work
echo "Installing the package in development mode..."
pip install -e .

# Add the current directory to PYTHONPATH to help with imports
echo "Setting PYTHONPATH..."
# Include all possible directories that might contain the modules
export PYTHONPATH=$PYTHONPATH:$(pwd):$(pwd)/..

# Check for backend directory and add to PYTHONPATH
if [ -d "../backend" ]; then
  echo "Adding backend directory to PYTHONPATH..."
  export PYTHONPATH=$PYTHONPATH:$(pwd)/../backend
fi

# Also add the parent of the backend directory
if [ -d "../backend" ]; then
  echo "Adding parent directory to PYTHONPATH..."
  export PYTHONPATH=$PYTHONPATH:$(pwd)/..
fi

echo "Current PYTHONPATH: $PYTHONPATH"
echo "Current directory structure (package directory):"
find . -type f -name "*.py" | sort

echo "Current directory structure (parent directory):"
find .. -maxdepth 2 -type f -name "*.py" | sort

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
