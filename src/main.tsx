
import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.tsx';
import './index.css';

console.log("Initializing application...");

try {
  const root = document.getElementById('root');
  if (root) {
    console.log("Root element found, rendering App");
    createRoot(root).render(
      <React.StrictMode>
        <App />
      </React.StrictMode>
    );
    console.log("App rendered successfully");
  } else {
    console.error("Root element not found");
  }
} catch (error) {
  console.error("Error initializing the application:", error);
}
