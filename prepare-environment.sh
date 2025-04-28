
#!/bin/bash
set -e

echo "=== Preparing environment for build ==="

# Check for Node.js and npm
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed. Please install Node.js first."
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "npm is not installed. Please install npm first."
    exit 1
fi

# Make all scripts executable
echo "Making scripts executable..."
chmod +x check-vite-deps.sh verify-environment.sh test-package.sh create-python-package.sh build-local.sh 2>/dev/null || true

# Clean existing files
echo "Cleaning environment..."
rm -rf node_modules package-lock.json npm-debug.log

# Clean npm cache
echo "Cleaning npm cache..."
npm cache clean --force

# Install dependencies with forced resolution
echo "Installing dependencies with forced resolution..."
npm install --legacy-peer-deps

# Explicitly install vite plugin with force flag
echo "Explicitly installing Vite plugin..."
npm install --force --save-dev @vitejs/plugin-react-swc

# Verify installation
echo "Verifying Vite plugin installation..."
if [ -d "node_modules/@vitejs/plugin-react-swc" ]; then
    echo "✓ @vitejs/plugin-react-swc is installed"
    ls -la node_modules/@vitejs/plugin-react-swc/
else
    echo "✗ @vitejs/plugin-react-swc installation failed"
    exit 1
fi

echo "=== Environment prepared successfully ==="
echo "You can now run ./test-package.sh or ./build-local.sh"
