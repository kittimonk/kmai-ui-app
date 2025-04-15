
# Knowledge Management AI - Deployment Guide

## Repository Preparation Checklist

### 1. Generate Package Lock File
```bash
# In project root directory
npm install
```
This creates `package-lock.json` which MUST be committed to the repository.

### 2. Required Files for Deployment
Ensure these files are present in the repository:
- Configuration Files:
  - `eslint.config.js`
  - `tailwind.config.ts`
  - `tsconfig.json`
  - `tsconfig.node.json`
  - `index.html`
  - `components.json`
  - `.gitignore`
  - `postcss.config.js`
  - `vite.config.ts`

- Deployment Scripts:
  - `deploy.sh`
  - `startup.sh`
  - `server.js`
  - `web.config`

- Dependency Files:
  - `package.json`
  - `package-lock.json`
  - `requirements.txt`
  - `api/requirements.txt`

### 3. Build Process
The build will:
- Generate `static` folder
- Create `.tar.gz` artifact
- Include all necessary files for deployment

### 4. Resolving Package Version Conflicts
In `requirements.txt` and `api/requirements.txt`, use version ranges:
```
# Before
fastapi==0.109.0

# After
fastapi>=0.109.0,<0.110.0
```

### 5. Azure Web App Configuration
- Python Runtime: 3.11+
- Operating System: Linux
- Ensure Application Settings configured:
  - `SCM_DO_BUILD_DURING_DEPLOYMENT`: `false`
  - `WEBSITE_RUN_FROM_PACKAGE`: `0`

### 6. Troubleshooting
If package installation fails:
```bash
pip install --no-cache-dir -r requirements.txt
```

## Deployment Workflow
1. Generate `package-lock.json`
2. Commit all required files
3. Push to repository
4. GitHub Actions will:
   - Build npm package
   - Create `.tar.gz` artifact
   - Deploy to Azure Web App

## Post-Deployment Verification
- Check Web App URL
- Verify chat and other features
- Review Azure Portal logs
