
#!/bin/bash
set -e

# Install test requirements first
pip install -r test-requirements.txt

# Make the script executable
chmod +x test-package.sh

# Install the package in development mode
pip install -e .

# Verify that the static directory exists and contains files
if [ ! -d "kmai_ent03_ui_app/static" ]; then
  echo "Creating kmai_ent03_ui_app/static directory"
  mkdir -p kmai_ent03_ui_app/static
fi

# Make sure static directory has at least one file
if [ ! -f "kmai_ent03_ui_app/static/index.html" ]; then
  echo "Creating placeholder index.html file"
  echo '<!DOCTYPE html><html><head><title>Test</title></head><body><h1>Test</h1></body></html>' > kmai_ent03_ui_app/static/index.html
fi

# Add the current directory to PYTHONPATH to help with imports
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Use either pytest or unittest, depending on what's installed
if command -v pytest &> /dev/null; then
  echo "Running tests with pytest..."
  python -m pytest tests/ -v
else
  echo "Running tests with unittest..."
  python -m unittest discover tests
fi

echo "Package tests completed successfully!"
