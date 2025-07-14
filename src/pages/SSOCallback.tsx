import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import { useAuthStore } from '@/services/auth';

const SSOCallback = () => {
  const [status, setStatus] = useState('Authenticating...');
  const navigate = useNavigate();
  const location = useLocation();
  const { setUser } = useAuthStore();

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    // If refresh=1, force a full reload to ensure session cookie is available
    if (params.get('refresh') === '1') {
      setStatus('Finalizing authentication...');
      window.location.replace('/');
      return;
    }

    const handleCallback = async () => {
      try {
        // Check if user is authenticated after SSO redirect
        const response = await fetch('/api/auth/status', {
          credentials: 'include'
        });
        
        if (response.ok) {
          const data = await response.json();
          if (data.isAuthenticated && data.user) {
            setUser(data.user);
            setStatus('Authentication successful! Redirecting...');
            setTimeout(() => {
              navigate('/');
            }, 1000);
          } else {
            setStatus('Authentication failed. Redirecting to login...');
            setTimeout(() => {
              navigate('/login');
            }, 2000);
          }
        } else {
          throw new Error('Authentication failed');
        }
      } catch (error) {
        console.error('SSO callback error:', error);
        setStatus('Authentication failed. Redirecting to login...');
        setTimeout(() => {
          navigate('/login');
        }, 2000);
      }
    };

    handleCallback();
  }, [navigate, setUser, location]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
        <p className="text-lg">{status}</p>
      </div>
    </div>
  );
};

export default SSOCallback;
