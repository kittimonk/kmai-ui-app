
import React from 'react';
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertTriangle } from 'lucide-react';
import { API_BASE_URL } from '@/config';

type ApiStatusAlertProps = {
  apiStatus: 'checking' | 'available' | 'unavailable';
};

const ApiStatusAlert = ({ apiStatus }: ApiStatusAlertProps) => {
  if (apiStatus !== 'unavailable') return null;
  
  return (
    <Alert variant="destructive" className="mb-6">
      <AlertTriangle className="h-4 w-4" />
      <AlertTitle>API Connection Error</AlertTitle>
      <AlertDescription>
        Cannot connect to API server. The application is running in offline mode with limited functionality.
        Please make sure the FastAPI server is running at {API_BASE_URL}
      </AlertDescription>
    </Alert>
  );
};

export default ApiStatusAlert;
