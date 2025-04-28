
import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.tsx';
import './index.css';

console.log("Initializing application...");

// Simple ErrorBoundary component for catching React errors
interface ErrorBoundaryProps {
  children: React.ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
}

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

// Store a reference to any created root to prevent multiple initializations
let rootInstance: any = null;

function initApp() {
  console.log("Initializing app...");
  
  try {
    const rootElement = document.getElementById('root');
    
    if (!rootElement) {
      console.error("Root element not found!");
      return;
    }
    
    console.log("Root element found with ID:", rootElement.id);
    
    // If we've already created a React root, don't create another one
    if (rootInstance) {
      console.log("React root already created, skipping initialization");
      return;
    }
    
    // Create a new React root
    console.log("Creating new React root...");
    rootInstance = createRoot(rootElement);
    
    // Render the application
    console.log("Rendering application...");
    rootInstance.render(
      <ErrorBoundary>
        <React.StrictMode>
          <App />
        </React.StrictMode>
      </ErrorBoundary>
    );
    
    console.log("Application rendered successfully");
  } catch (error) {
    console.error("Error during app initialization:", error);
  }
}

// Initialize the application
if (document.readyState === "loading") {
  console.log("Document still loading, waiting for DOMContentLoaded");
  document.addEventListener("DOMContentLoaded", initApp);
} else {
  console.log("Document already loaded, initializing immediately");
  initApp();
}

// Global error handler
window.addEventListener('error', (event) => {
  console.error("Global error caught:", event.error);
});
