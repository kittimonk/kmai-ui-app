
#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

# Build the Vite app to static directory
echo "Building Vite app to static directory..."
npm ci
npx vite build

# Ensure static directory exists
if [ -d "static" ]; then
  echo "Static folder successfully created."
else
  echo "ERROR: Static folder was not created. Build process may have failed."
  exit 1
fi

# Create egg-info directory with all required files
echo "Creating egg-info directory with required files..."
mkdir -p kmai_ent03_ui_app.egg-info
touch kmai_ent03_ui_app.egg-info/PKG-INFO
touch kmai_ent03_ui_app.egg-info/SOURCES.txt
touch kmai_ent03_ui_app.egg-info/dependency_links.txt
touch kmai_ent03_ui_app.egg-info/not-zip-safe
touch kmai_ent03_ui_app.egg-info/top_level.txt

# Create requires.txt with proper content
echo "Creating requires.txt with proper content..."
cat > kmai_ent03_ui_app.egg-info/requires.txt << 'EOL'
fastapi==0.109.0
uvicorn==0.27.0
python-jose==3.3.0
requests==2.31.0
python-multipart==0.0.6
sentence-transformers==2.2.2
scikit-learn==1.3.2
azure-storage-file-datalake==12.12.0
azure-storage-blob==12.18.0
azure-identity==1.14.0
azure-mgmt-cognitiveservices==13.5.0
openai==1.10.0
numpy==1.26.0
httpx==0.24.1
redis==5.0.1
pyodbc==5.0.1
striprtf==0.0.18
azure-search-documents==11.4.0
EOL

# Create top_level.txt with proper content
echo "Creating top_level.txt with proper content..."
echo "backend" > kmai_ent03_ui_app.egg-info/top_level.txt

echo "Local build complete! The following files have been created:"
ls -la static/
echo "Egg-info directory:"
ls -la kmai_ent03_ui_app.egg-info/

echo "You can now commit these files to your repository:"
echo "- static/ directory"
echo "- kmai_ent03_ui_app.egg-info/ directory"
echo "- All Python-related files (setup.py, requirements.txt, etc.)"
