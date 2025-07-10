
// API configuration

// For local development, use your local FastAPI server
const LOCAL_API_URL = 'http://localhost:8000';

// For Azure Web App environment
const AZURE_API_URL = ''; #No /api prefix

// Determine if running on Azure Web App
const isAzureEnvironment = window.location.hostname.includes('azurewebsites.net')  || window.location.hostname === "kme03.dev.com";

// For Lovable preview environment
const isLovableEnvironment = window.location.hostname.includes('lovableproject.com') || window.location.hostname.includes('lovable.app');

// Export the API base URL based on the environment
export const API_BASE_URL = isAzureEnvironment ? 
                           AZURE_API_URL : 
                           (isLovableEnvironment ? 'https://mock-api-chat.lovableproject.com' : LOCAL_API_URL);

// Other global configuration variables can be added here
