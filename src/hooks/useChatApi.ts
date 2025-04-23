
import { useState, useEffect } from 'react';
import { toast } from "sonner";
import { Message } from '../types/chat';
import { API_BASE_URL } from '../config';

export const useChatApi = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);
  const [apiStatus, setApiStatus] = useState<'checking' | 'available' | 'unavailable'>('checking');
  const [isLovablePreview] = useState(window.location.hostname.includes('lovableproject.com') || window.location.hostname.includes('lovable.app'));

  // Check API availability on hook mount
  useEffect(() => {
    checkApiAvailability();
  }, []);

  const checkApiAvailability = async () => {
    if (isLovablePreview) {
      // In Lovable preview, we'll use mock responses instead of showing an error
      console.log("Running in Lovable preview mode - using mock responses");
      setApiError(null);
      setApiStatus('available');
      return;
    }
    
    try {
      console.log(`Checking API availability at ${API_BASE_URL}/api/health`);
      const response = await fetch(`${API_BASE_URL}/api/health`, { 
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });
      
      if (response.ok) {
        console.log("API connection successful");
        setApiError(null);
        setApiStatus('available');
      } else {
        console.error(`API responded with status: ${response.status}`);
        setApiError('API is not responding correctly');
        setApiStatus('unavailable');
      }
    } catch (error) {
      console.error("API availability check failed:", error);
      setApiError(`Cannot connect to API server at ${API_BASE_URL}`);
      setApiStatus('unavailable');
    }
  };

  // Retry API connection
  const retryApiConnection = () => {
    setApiStatus('checking');
    checkApiAvailability();
    toast.info("Checking API connection...");
  };

  return {
    isLoading,
    setIsLoading,
    apiError,
    setApiError,
    apiStatus,
    isLovablePreview,
    checkApiAvailability,
    retryApiConnection
  };
};
