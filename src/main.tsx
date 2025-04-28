
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
console.log("Current URL:", window.location.href);
console.log("Current hostname:", window.location.hostname);

// Define proper TypeScript interfaces for the error boundary
interface ErrorBoundaryProps {
  children: React.ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
}

// Create a simple error boundary component for debugging
class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error, errorInfo: null };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    console.error("React Error Boundary caught an error:", error);
    console.error("Component stack:", errorInfo.componentStack);
    this.setState({ errorInfo });
  }

  render(): React.ReactNode {
    if (this.state.hasError) {
      return (
        <div style={{ margin: '20px', padding: '20px', border: '1px solid red', color: 'red' }}>
          <h2>Something went wrong.</h2>
          <details style={{ whiteSpace: 'pre-wrap' }}>
            {this.state.error && this.state.error.toString()}
            <br />
            {this.state.errorInfo && this.state.errorInfo.componentStack}
          </details>
        </div>
      );
    }

    return this.props.children;
  }
}

// Track if we've already created a root to prevent duplicate roots
let reactRoot;

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
      console.log("Root element properties:", {
        id: root.id,
        tagName: root.tagName,
        childNodes: root.childNodes.length,
      });
      
      // Only check for React's data-reactroot attribute to avoid double React instances
      // Removed check for root.childNodes.length > 0 to allow rendering in Lovable preview
      if (root.hasAttribute('data-reactroot')) {
        console.log("Root already has React instance - skipping duplicate render");
        return;
      }
      
      // Create React root with additional error logging
      try {
        // Only create a new root if we haven't already
        if (!reactRoot) {
          reactRoot = createRoot(root);
          console.log("React root created successfully");
        }
        
        // Attempt to render with detailed reporting
        try {
          reactRoot.render(
            <ErrorBoundary>
              <React.StrictMode>
                <App />
              </React.StrictMode>
            </ErrorBoundary>
          );
          console.log("App rendered successfully");
          
          // Add a post-render check
          setTimeout(() => {
            console.log("Post-render check: Root children count:", root.childNodes.length);
            console.log("App mounted successfully");
          }, 100);
          
        } catch (renderError) {
          console.error("Error rendering the App:", renderError);
          // Try rendering a minimal app to see if the issue is with the App component
          try {
            reactRoot.render(<div>Minimal App Test</div>);
            console.log("Minimal app rendered successfully - issue is likely with App component");
          } catch (minimalError) {
            console.error("Even minimal app failed to render:", minimalError);
          }
        }
      } catch (rootError) {
        console.error("Error creating React root:", rootError);
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
  
  // Check if App was successfully mounted after window load
  const rootElement = document.getElementById('root');
  if (rootElement) {
    console.log("Window loaded: Root element children count:", rootElement.childNodes.length);
  }
});
