
import React from 'react';
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { API_BASE_URL } from '@/config';

type ApiStatusAlertProps = {
  apiStatus: 'checking' | 'available' | 'unavailable';
  onRetry?: () => void;
};

const ApiStatusAlert = ({ apiStatus, onRetry }: ApiStatusAlertProps) => {
  if (apiStatus === 'available') return null;
  
  return (
    <Alert variant={apiStatus === 'checking' ? "default" : "destructive"} className="mb-6">
      <AlertTriangle className="h-4 w-4" />
      <AlertTitle>
        {apiStatus === 'checking' ? 'Checking API Connection...' : 'API Connection Error'}
      </AlertTitle>
      <AlertDescription className="flex justify-between items-center">
        <span>
          {apiStatus === 'checking' 
            ? `Verifying connection to API server at ${API_BASE_URL}`
            : `Cannot connect to API server. Please make sure the FastAPI server is running at ${API_BASE_URL}`
          }
        </span>
        
        {onRetry && apiStatus === 'unavailable' && (
          <button 
            onClick={onRetry}
            className="mt-2 flex items-center text-xs px-2 py-1 bg-white/10 rounded hover:bg-white/20"
          >
            <RefreshCw size={12} className="mr-1" />
            Retry
          </button>
        )}
      </AlertDescription>
    </Alert>
  );
};

export default ApiStatusAlert;
