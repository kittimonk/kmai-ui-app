
#!/bin/bash
set -e

echo "Checking for Vite plugin dependencies..."

# Check if node_modules directory exists
if [ ! -d "node_modules" ]; then
  echo "ERROR: node_modules directory does not exist!"
  echo "Please run 'npm install' first."
  exit 1
fi

# Check if Vite plugin directory exists
if [ ! -d "node_modules/@vitejs/plugin-react-swc" ]; then
  echo "ERROR: @vitejs/plugin-react-swc is missing!"
  echo "Installing it now..."
  
  # Try installation with different methods
  echo "Attempt 1: Using npm install --save-dev"
  if npm install --save-dev @vitejs/plugin-react-swc; then
    echo "SUCCESS: @vitejs/plugin-react-swc has been installed."
  else
    echo "First attempt failed, trying alternative installation method..."
    echo "Attempt 2: Using npm install --no-save"
    if npm install --no-save @vitejs/plugin-react-swc; then
      echo "SUCCESS: @vitejs/plugin-react-swc has been installed with --no-save option."
    else
      echo "FAILED: @vitejs/plugin-react-swc installation failed after multiple attempts!"
      echo "Try installing it manually with: npm install --save-dev @vitejs/plugin-react-swc"
      
      # Check for common issues
      echo "Checking for common issues..."
      if [ ! -f "package.json" ]; then
        echo "ERROR: package.json is missing!"
      fi
      
      # Check npm registry accessibility
      echo "Checking npm registry accessibility..."
      if ! npm ping; then
        echo "ERROR: Cannot access npm registry. Check your internet connection."
      fi
      
      exit 1
    fi
  fi
  
  # Verify installation
  if [ -d "node_modules/@vitejs/plugin-react-swc" ]; then
    echo "VERIFICATION: @vitejs/plugin-react-swc directory exists."
    ls -la node_modules/@vitejs/plugin-react-swc/
  else
    echo "VERIFICATION FAILED: @vitejs/plugin-react-swc directory still missing!"
    exit 1
  fi
else
  echo "SUCCESS: @vitejs/plugin-react-swc is properly installed."
  ls -la node_modules/@vitejs/plugin-react-swc/
fi

# Check for lovable-tagger
if [ ! -d "node_modules/lovable-tagger" ]; then
  echo "WARNING: lovable-tagger module is missing!"
  echo "This might cause errors if it's required by your configuration."
fi

echo "Dependency check completed."
