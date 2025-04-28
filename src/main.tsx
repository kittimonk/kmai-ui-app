
import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.tsx';
import './index.css';

console.log("Initializing application with detailed logging...");

// Helper function to check if we're running in a Lovable preview environment
const isLovablePreview = () => {
  return window.location.hostname.includes('lovableproject.com') || 
         window.location.hostname.includes('lovable.app');
};

console.log("Running in Lovable preview:", isLovablePreview());

// Check if the DOM is ready
if (document.readyState === 'loading') {
  console.log("Document is still loading, waiting for DOMContentLoaded");
  document.addEventListener('DOMContentLoaded', initApp);
} else {
  console.log("Document is ready, initializing app immediately");
  initApp();
}

function initApp() {
  try {
    console.log("Finding root element...");
    const root = document.getElementById('root');
    
    if (root) {
      console.log("Root element found, rendering App");
      
      // Wrap the render in a try-catch to catch any rendering errors
      try {
        createRoot(root).render(
          <React.StrictMode>
            <App />
          </React.StrictMode>
        );
        console.log("App rendered successfully");
      } catch (renderError) {
        console.error("Error rendering the App:", renderError);
      }
    } else {
      console.error("Root element not found. DOM structure:", document.body.innerHTML);
    }
  } catch (error) {
    console.error("Critical error initializing the application:", error);
  }
}

// Add a global error handler to catch unhandled errors
window.addEventListener('error', (event) => {
  console.error("Unhandled global error:", event.error);
});

// Log when the window has fully loaded
window.addEventListener('load', () => {
  console.log("Window fully loaded");
});

