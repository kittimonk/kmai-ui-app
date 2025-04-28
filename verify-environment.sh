
#!/bin/bash
set -e

echo "=== Environment Verification Script ==="
echo "Checking system information..."
echo "Node.js version: $(node -v)"
echo "npm version: $(npm -v)"
echo "Python version: $(python --version)"

echo "=== Checking package.json dependencies ==="
if [ ! -f "package.json" ]; then
  echo "ERROR: package.json not found!"
  exit 1
fi

# Check if the vital Vite plugin is in package.json
if grep -q "@vitejs/plugin-react-swc" package.json; then
  echo "✓ @vitejs/plugin-react-swc found in package.json"
else
  echo "✗ ERROR: @vitejs/plugin-react-swc NOT found in package.json"
  echo "This is likely causing your build issues!"
fi

echo "=== Checking node_modules directory ==="
if [ ! -d "node_modules" ]; then
  echo "✗ ERROR: node_modules directory does not exist!"
else
  echo "✓ node_modules directory exists"
  
  if [ -d "node_modules/@vitejs/plugin-react-swc" ]; then
    echo "✓ @vitejs/plugin-react-swc directory exists in node_modules"
    
    # List files to verify it's not empty
    echo "Files in plugin directory:"
    ls -la node_modules/@vitejs/plugin-react-swc/
  else
    echo "✗ ERROR: @vitejs/plugin-react-swc directory missing in node_modules!"
  fi
fi

echo "=== Checking for temporary/lock files ==="
if [ -f "package-lock.json" ]; then
  echo "package-lock.json exists"
fi

if [ -f "npm-debug.log" ]; then
  echo "WARNING: npm-debug.log exists - this may indicate previous installation issues"
  echo "Content of npm-debug.log:"
  cat npm-debug.log
fi

echo "=== Verification complete ==="
echo "If issues persist, try running:"
echo "rm -rf node_modules package-lock.json"
echo "npm install"
echo "npm install --save-dev @vitejs/plugin-react-swc"
