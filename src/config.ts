// API configuration

// For local development, use your local FastAPI server
const LOCAL_API_URL = 'http://localhost:3000';

// For Azure Web App environment
const AZURE_API_URL = '/api'; 

// Determine if running on Azure Web App
const isAzureEnvironment = window.location.hostname.includes('azurewebsites.net');

// For Lovable preview environment
const isLovableEnvironment = window.location.hostname.includes('lovableproject.com');

// Export the API base URL based on the environment
export const API_BASE_URL = isAzureEnvironment ? 
                           AZURE_API_URL : 
                           (isLovableEnvironment ? 'https://mock-api-chat.lovableproject.com' : LOCAL_API_URL);

// Other global configuration variables can be added here
