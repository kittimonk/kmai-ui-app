
#!/bin/bash
set -e

echo "=== Environment Verification Script ==="
echo "Checking system information..."
echo "Node.js version: $(node -v)"
echo "npm version: $(npm -v)"
echo "Python version: $(python --version)"
echo "OS information: $(uname -a)"
echo "Current directory: $(pwd)"

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
  echo "Adding it to package.json..."
  # Use npm to add the dependency
  npm install --save-dev @vitejs/plugin-react-swc
  if grep -q "@vitejs/plugin-react-swc" package.json; then
    echo "✓ Successfully added @vitejs/plugin-react-swc to package.json"
  else
    echo "✗ Failed to add @vitejs/plugin-react-swc to package.json"
  fi
fi

echo "=== Checking npm configuration ==="
echo "npm config list:"
npm config list

echo "=== Checking for network issues ==="
echo "Testing npm registry connection..."
if npm ping; then
  echo "✓ npm registry is accessible"
else
  echo "✗ Cannot connect to npm registry. Check your internet connection or proxy settings."
fi

echo "=== Checking node_modules directory ==="
if [ ! -d "node_modules" ]; then
  echo "✗ ERROR: node_modules directory does not exist!"
  echo "Attempting to create it with a fresh install..."
  npm install
else
  echo "✓ node_modules directory exists"
  
  if [ -d "node_modules/@vitejs/plugin-react-swc" ]; then
    echo "✓ @vitejs/plugin-react-swc directory exists in node_modules"
    
    # List files to verify it's not empty
    echo "Files in plugin directory:"
    ls -la node_modules/@vitejs/plugin-react-swc/
  else
    echo "✗ ERROR: @vitejs/plugin-react-swc directory missing in node_modules!"
    echo "Attempting direct installation..."
    npm install --no-save @vitejs/plugin-react-swc
    
    # Check again after installation attempt
    if [ -d "node_modules/@vitejs/plugin-react-swc" ]; then
      echo "✓ Successfully installed @vitejs/plugin-react-swc"
    else
      echo "✗ Installation attempt failed"
    fi
  fi
fi

echo "=== Checking Vite configuration ==="
if [ -f "vite.config.ts" ]; then
  echo "✓ vite.config.ts exists"
  echo "Content of vite.config.ts:"
  cat vite.config.ts
else
  echo "✗ ERROR: vite.config.ts not found!"
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

echo "=== Suggested troubleshooting steps ==="
echo "If issues persist, try running:"
echo "rm -rf node_modules package-lock.json"
echo "npm cache clean --force"
echo "npm install --legacy-peer-deps"
echo "npm install --save-dev @vitejs/plugin-react-swc"
echo "or try directly: npx npm@latest install --save-dev @vitejs/plugin-react-swc"

echo "=== Verification complete ==="
