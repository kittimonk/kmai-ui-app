
import React from 'react';
import { AlertTriangle, RotateCcw } from 'lucide-react';

type ApiErrorBannerProps = {
  error: string;
  apiBaseUrl: string;
  onRetry: () => void;
};

const ApiErrorBanner = ({ error, apiBaseUrl, onRetry }: ApiErrorBannerProps) => {
  if (!error) return null;
  
  return (
    <div className="p-3 bg-red-50 border-b border-red-200 text-red-700 flex justify-between items-center">
      <div className="flex items-center">
        <AlertTriangle className="mr-2" size={16} />
        <span>{error}. Please make sure the FastAPI server is running at {apiBaseUrl}.</span>
      </div>
      <button 
        onClick={onRetry}
        className="p-1 bg-red-100 rounded-lg hover:bg-red-200 transition-colors"
      >
        <RotateCcw size={16} />
      </button>
    </div>
  );
};

export default ApiErrorBanner;
