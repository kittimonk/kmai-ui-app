
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

// Initialize the app with enhanced error handling
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
      
      // IMPORTANT: In Lovable preview, we need to render our app regardless of existing content
      // Only check if there's already a React instance to avoid conflicts
      const hasReactInstance = root.hasAttribute('data-reactroot');
      
      if (hasReactInstance) {
        console.log("Root already has React instance - skipping duplicate render");
        return;
      }
      
      // Create and render the app
      try {
        console.log("Creating React root...");
        const reactRoot = createRoot(root);
        console.log("React root created successfully");
        
        // Render with error boundary
        try {
          console.log("Rendering app...");
          reactRoot.render(
            <ErrorBoundary>
              <React.StrictMode>
                <App />
              </React.StrictMode>
            </ErrorBoundary>
          );
          console.log("App rendered successfully");
          
          // Verify render
          setTimeout(() => {
            console.log("Post-render check: Root has React content:", root.hasAttribute('data-reactroot'));
            console.log("App mounted successfully");
          }, 100);
          
        } catch (renderError) {
          console.error("Error rendering the App:", renderError);
        }
      } catch (rootError) {
        console.error("Error creating React root:", rootError);
      }
    } else {
      console.error("Root element not found!");
    }
  } catch (error) {
    console.error("Critical error initializing the application:", error);
  }
}

// Check if DOM is ready and initialize app
if (document.readyState === 'loading') {
  console.log("Document is still loading, waiting for DOMContentLoaded");
  document.addEventListener('DOMContentLoaded', initApp);
} else {
  console.log("Document is ready, initializing app immediately");
  initApp();
}

// Add a global error handler
window.addEventListener('error', (event) => {
  console.error("Unhandled global error:", event.error);
});

// Log when window is fully loaded
window.addEventListener('load', () => {
  console.log("Window fully loaded");
  
  // Verify app is mounted after window load
  const rootElement = document.getElementById('root');
  if (rootElement) {
    console.log("Window loaded: Root element children count:", rootElement.childNodes.length);
  }
});
