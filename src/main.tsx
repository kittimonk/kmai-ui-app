
import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.tsx';
import './index.css';

try {
  const root = document.getElementById('root');
  if (root) {
    createRoot(root).render(
      <React.StrictMode>
        <App />
      </React.StrictMode>
    );
  } else {
    console.error("Root element not found");
  }
} catch (error) {
  console.error("Error initializing the application:", error);
}
