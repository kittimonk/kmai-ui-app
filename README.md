
# Knowledge Management AI Application - Azure Deployment Guide

## Project info

**URL**: https://lovable.dev/projects/90a9e865-27ff-4a0c-bffb-140c91052bf2

## Repository Structure for Deployment

The repository should be structured as follows for successful deployment:

```
knowledge-management-ai/
├── api/                   # FastAPI backend code
│   ├── main.py           # Main FastAPI application
│   └── requirements.txt  # Python dependencies
├── src/                   # React frontend code
│   └── ...               # React components and utilities
├── public/                # Static assets
├── deploy.sh              # Deployment script
├── server.js              # Express server for production
├── startup.sh             # Azure startup script
├── web.config             # Azure Web App configuration
├── .deployment            # Azure deployment configuration
├── requirements.txt       # Root-level Python dependencies
├── package.json           # Node.js dependencies
├── vite.config.ts         # Vite configuration
└── tsconfig.json          # TypeScript configuration
```

## Deployment Steps

### 1. Preparing the Repository

1. Create a new Git repository with the structure above.
2. Ensure all source files are copied to their respective directories.
3. **Critical**: Generate the `package-lock.json` file before pushing:
   ```sh
   npm install
   ```
   This creates the necessary `package-lock.json` file required by your organization's CI process.

### 2. CI Process (Artifact Creation)

Your organization's GitHub Actions workflow will:

1. Clone the repository
2. Install dependencies specified in package.json
3. Build the React application with Vite
4. Package the built files as a .tar.gz artifact
5. Push the artifact to Nexus

#### Build Process Configuration

Ensure your `package.json` has the following scripts:

```json
"scripts": {
  "build": "vite build",
  "postbuild": "node deploy.sh"
}
```

The `deploy.sh` script handles:
- Building the Vite app to the static directory
- Creating the server.js file for production
- Installing Express and http-proxy-middleware

### 3. CD Process (Azure Deployment)

For the CD process, you'll need to provide:

1. Azure Web App resource name
2. Subscription ID
3. Environment (dev)
4. App Service Plan details

Your workflow will:
1. Fetch the artifact from Nexus
2. Deploy to the Azure Web App
3. Execute the startup script

### 4. Azure Web App Configuration

#### Runtime Configuration
- Python version: 3.11 or above
- Node.js: Ensure it's available in the App Service
- OS: Linux

#### Web App Settings

Add these Application Settings in Azure Portal:
- `SCM_DO_BUILD_DURING_DEPLOYMENT`: set to `false` (since build happens in CI)
- `WEBSITE_RUN_FROM_PACKAGE`: set to `0`

### 5. Starting Both Frontend and Backend

The `startup.sh` script handles:
1. Installing Node.js dependencies
2. Installing Python dependencies
3. Starting the FastAPI backend on port 3000
4. Starting the Express server to serve static files and proxy API requests

### 6. Troubleshooting Common Issues

#### Package Version Issues

If you encounter "no matching distribution found" errors:

1. Check the `requirements.txt` files (both root and in api/ folder)
2. Replace specific version constraints with compatible ranges:
   ```
   # Instead of
   fastapi==0.109.0
   
   # Use
   fastapi>=0.109.0,<0.110.0
   ```

3. For Python package conflicts, consider using:
   ```
   pip install --no-cache-dir -r requirements.txt
   ```

#### API Connection Issues

If the chat feature doesn't work after deployment:

1. Check the `config.ts` file to ensure proper API URL configuration
2. Verify the `API_BASE_URL` is correctly set for the Azure environment
3. Ensure the proxying in `server.js` is configured correctly:
   ```javascript
   app.use('/api', createProxyMiddleware({
     target: 'http://localhost:3000',
     changeOrigin: true
   }));
   ```

#### Deployment Script Issues

Ensure all scripts have proper permissions:
```sh
git update-index --chmod=+x deploy.sh
git update-index --chmod=+x startup.sh
```

### 7. Final Verification

After deployment:
1. Access your web app URL
2. Verify all features are working
3. Check logs through Azure Portal (Log stream)
4. Test the chat feature to ensure FastAPI backend is running correctly

## Important Files to Check Before Deployment

1. `src/config.ts` - Ensure proper API URL configuration
2. `server.js` - Verify correct proxying of API requests
3. `startup.sh` - Check service startup configuration
4. `web.config` - Verify Azure Web App configuration
5. `api/main.py` - Check FastAPI configuration
6. `requirements.txt` - Ensure compatible Python dependencies
7. `package.json` - Verify Node.js dependencies

## Post-Deployment Monitoring

1. Set up Application Insights for monitoring
2. Configure alerts for critical failures
3. Regularly check API health endpoints (/api/health)

## Security Considerations

1. Ensure Azure Managed Identity is correctly configured
2. Verify CORS settings in FastAPI
3. Check that sensitive configuration is stored in Azure App Settings, not in code

By following these steps, you should be able to successfully deploy your Knowledge Management AI application to Azure Web App using your organization's GitHub Actions workflows.
