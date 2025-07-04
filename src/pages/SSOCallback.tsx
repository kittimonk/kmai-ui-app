import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { authService } from '../services/authService';
import { Loader2 } from 'lucide-react';
import { checkAuthStatus } from '@/services/auth'; // ✅ Import the fix

const AuthCallback = () => {
  const [status, setStatus] = useState('Authenticating...');
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const handleAuth = async () => {
      const searchParams = new URLSearchParams(location.search);
      const code = searchParams.get('code');

      if (!code) {
        setStatus('Error: No authorization code found in the URL');
        setTimeout(() => navigate('/'), 3000);
        return;
      }

      try {
        setStatus('Processing authentication...');

        // ✅ Call backend SSO handler (optional for logging)
        await authService.handleCallback();

        // ✅ Fetch user session from backend and update Zustand
        await checkAuthStatus();

        setStatus('Authentication successful! Redirecting...');
        setTimeout(() => navigate('/chat'), 1500);
      } catch (error) {
        console.error('Error during authentication:', error);
        setStatus(`Authentication error: ${error instanceof Error ? error.message : 'Unknown error'}`);
        setTimeout(() => navigate('/'), 3000);
      }
    };

    handleAuth();
  }, [location, navigate]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 px-4">
      <div className="w-full max-w-md p-8 space-y-6 bg-white rounded-xl shadow-lg">
        <div className="flex flex-col items-center justify-center space-y-4">
          <Loader2 className="h-12 w-12 text-green-700 animate-spin" />
          <h1 className="text-2xl font-bold text-gray-900">SSO Authentication</h1>
          <p className="text-gray-600 text-center">{status}</p>
        </div>
      </div>
    </div>
  );
};

export default AuthCallback;
