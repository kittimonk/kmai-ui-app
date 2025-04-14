
import { useState, useEffect } from 'react';
import { toast } from "sonner";
import { Message } from '../types/chat';
import { API_BASE_URL } from '../config';

export const useChatApi = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);
  const [isLovablePreview] = useState(window.location.hostname.includes('lovableproject.com'));

  // Check API availability on hook mount
  useEffect(() => {
    checkApiAvailability();
  }, []);

  const checkApiAvailability = async () => {
    if (isLovablePreview) {
      // In Lovable preview, we'll simulate API availability
      setApiError(null);
      return;
    }
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/health`, { 
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });
      
      if (response.ok) {
        setApiError(null);
      } else {
        setApiError('API is not responding correctly');
      }
    } catch (error) {
      console.error("API availability check failed:", error);
      setApiError(`Cannot connect to API server at ${API_BASE_URL}`);
    }
  };

  // Retry API connection
  const retryApiConnection = () => {
    checkApiAvailability();
    toast.info("Checking API connection...");
  };

  return {
    isLoading,
    setIsLoading,
    apiError,
    setApiError,
    isLovablePreview,
    checkApiAvailability,
    retryApiConnection
  };
};
