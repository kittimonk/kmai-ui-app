
#!/bin/bash
set -e

echo "=== Preparing environment for build ==="
echo "Node version: $(node -v)"
echo "NPM version: $(npm -v)"

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

# Install dependencies
echo "Installing dependencies..."
npm install --legacy-peer-deps

# Check if vite plugin was installed correctly
echo "Checking for Vite plugin installation..."
if [ ! -d "node_modules/@vitejs/plugin-react-swc" ]; then
    echo "Vite plugin not found after initial installation. Attempting direct installation..."
    # Try multiple installation methods
    echo "Method 1: Using --save-dev"
    npm install --save-dev @vitejs/plugin-react-swc || true
    
    echo "Method 2: Using --no-save"
    npm install --no-save @vitejs/plugin-react-swc || true
    
    echo "Method 3: Using --force"
    npm install --force --save-dev @vitejs/plugin-react-swc || true
    
    # Final check
    if [ ! -d "node_modules/@vitejs/plugin-react-swc" ]; then
        echo "All automatic installation methods failed. Trying direct download..."
        
        # Create directory structure if it doesn't exist
        mkdir -p node_modules/@vitejs/
        
        # Use npm pack to get the package tarball
        echo "Using npm pack to get the package..."
        TMPDIR=$(mktemp -d)
        cd $TMPDIR
        npm pack @vitejs/plugin-react-swc
        PACKAGE=$(ls *.tgz)
        tar -xzf $PACKAGE
        cd -
        
        # Move the extracted package to node_modules
        if [ -d "$TMPDIR/package" ]; then
            echo "Moving extracted package to node_modules..."
            mv "$TMPDIR/package" node_modules/@vitejs/plugin-react-swc
        else
            echo "Failed to extract package."
            exit 1
        fi
        
        # Cleanup
        rm -rf $TMPDIR
    fi
fi

# Verify installation
echo "Verifying Vite plugin installation..."
if [ -d "node_modules/@vitejs/plugin-react-swc" ]; then
    echo "✓ @vitejs/plugin-react-swc is installed"
    ls -la node_modules/@vitejs/plugin-react-swc/
    
    # Check package.json to make sure the dependency is listed
    if ! grep -q "@vitejs/plugin-react-swc" package.json; then
        echo "Adding @vitejs/plugin-react-swc to package.json..."
        # Use a temporary file to avoid issues with direct in-place editing
        npm install --save-dev @vitejs/plugin-react-swc
    fi
else
    echo "✗ @vitejs/plugin-react-swc installation failed"
    echo "Detailed diagnostics:"
    echo "Contents of node_modules/@vitejs directory (if it exists):"
    ls -la node_modules/@vitejs/ 2>/dev/null || echo "Directory does not exist"
    
    echo "NPM debug logs:"
    cat npm-debug.log 2>/dev/null || echo "No debug logs found"
    
    echo "Please try installing manually with: npm install --save-dev @vitejs/plugin-react-swc"
    exit 1
fi

echo "=== Environment prepared successfully ==="
echo "You can now run ./test-package.sh or ./build-local.sh"
