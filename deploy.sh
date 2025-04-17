
#!/bin/bash

# Script checks if static directory exists
if [ ! -d "static" ]; then
  echo "ERROR: Static directory not found. Please run 'npm run build' locally first."
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
include static/*
recursive-include static *
recursive-include backend *
include setup.py
EOL

# List files being included in the package
echo "Files included in the package:"
find . -type f \( -name "*.py" -o -name "*.txt" -o -path "./static/*" \) -not -path "./node_modules/*" -not -path "./src/*"

echo "The package is ready for deployment."
