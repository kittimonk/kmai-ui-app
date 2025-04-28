
import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { API_BASE_URL } from '@/config';

type ApiStatusAlertProps = {
  status: 'checking' | 'available' | 'unavailable';
  onRetry: () => void;
};

const ApiStatusAlert = ({ status, onRetry }: ApiStatusAlertProps) => {
  if (status === 'available') {
    return null;
  }

  return (
    <div className={`mb-6 p-4 rounded-lg border ${status === 'checking' ? 'bg-yellow-50 border-yellow-200' : 'bg-red-50 border-red-200'}`}>
      <div className="flex items-start">
        <div className="shrink-0">
          <AlertCircle className={`h-5 w-5 ${status === 'checking' ? 'text-yellow-500' : 'text-red-500'}`} />
        </div>
        <div className="ml-3 flex-1">
          <h3 className={`text-sm font-medium ${status === 'checking' ? 'text-yellow-800' : 'text-red-800'}`}>
            {status === 'checking' ? 'Checking API connection...' : 'API connection unavailable'}
          </h3>
          <div className={`mt-2 text-sm ${status === 'checking' ? 'text-yellow-700' : 'text-red-700'}`}>
            {status === 'checking' ? (
              <p>Please wait while we verify the API connection.</p>
            ) : (
              <p>
                Cannot connect to the API server at {API_BASE_URL}. The code explainer will work in offline mode 
                with simulated responses. For full functionality, please start the FastAPI server.
              </p>
            )}
          </div>
          {status === 'unavailable' && (
            <div className="mt-4">
              <Button 
                variant="outline" 
                size="sm" 
                onClick={onRetry}
                className="flex items-center"
              >
                <RefreshCw className="mr-2 h-4 w-4" />
                Retry Connection
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ApiStatusAlert;
