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

// Initialize the application
console.log("Starting application initialization...");

try {
  const rootElement = document.getElementById('root');
  
  if (!rootElement) {
    console.error("Root element not found! Unable to mount the application.");
    throw new Error("Missing root element");
  }

  console.log("Root element found with ID:", rootElement.id);
  
  // Create and render the application
  console.log("Creating React root and rendering application...");
  const root = createRoot(rootElement);
  root.render(
    <ErrorBoundary>
      <React.StrictMode>
        <App />
      </React.StrictMode>
    </ErrorBoundary>
  );
  
  console.log("Application rendered successfully");
} catch (error) {
  console.error("Fatal error during application initialization:", error);
}

// Global error handler
window.addEventListener('error', (event) => {
  console.error("Global error caught:", event.error);
});

console.log("Application initialization complete");
