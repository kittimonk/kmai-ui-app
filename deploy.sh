
#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

# Script checks if static directory exists
if [ ! -d "static" ]; then
  echo "ERROR: Static directory not found."
  echo "Please run 'npm run build' locally first to generate the static directory."
  exit 1
fi

# Check if static directory has content and index.html exists
if [ -z "$(ls -A static 2>/dev/null)" ] || [ ! -f "static/index.html" ]; then
  echo "ERROR: Static directory is empty or missing index.html."
  echo "Please run 'npm run build' locally first to generate the static content."
  echo "Static directory contents:"
  ls -la static/
  exit 1
fi

# Script checks if egg-info directory exists
if [ ! -d "kmai_ent03_ui_app.egg-info" ]; then
  echo "ERROR: egg-info directory not found. Please run setup.py locally first."
  exit 1
fi

# Create MANIFEST.in file
echo "Creating MANIFEST.in file..."
cat > MANIFEST.in << 'EOL'
include requirements.txt
include backend/requirements.txt
include static/index.html
recursive-include static *
recursive-include backend *
include setup.py
include package.json
include package-lock.json
include server.js
include startup.sh
include web.config
EOL

# Check package contents before deployment
echo "Files included in the package:"
find . -type f \( -name "*.py" -o -name "*.txt" -o -path "./static/*" -o -name "*.js" -o -name "*.json" -o -name "*.config" -o -name "*.sh" \) -not -path "./node_modules/*" -not -path "./src/*" -not -path "./.git/*" | sort

echo "The package is ready for deployment."
