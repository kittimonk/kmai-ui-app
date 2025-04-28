
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
  npm install --save-dev @vitejs/plugin-react-swc
  
  # Verify installation
  if [ -d "node_modules/@vitejs/plugin-react-swc" ]; then
    echo "SUCCESS: @vitejs/plugin-react-swc has been installed."
  else
    echo "FAILED: @vitejs/plugin-react-swc installation failed!"
    exit 1
  fi
else
  echo "SUCCESS: @vitejs/plugin-react-swc is properly installed."
fi

# Check for lovable-tagger
if [ ! -d "node_modules/lovable-tagger" ]; then
  echo "WARNING: lovable-tagger module is missing!"
  echo "This might cause errors if it's required by your configuration."
fi

echo "Dependency check completed."
