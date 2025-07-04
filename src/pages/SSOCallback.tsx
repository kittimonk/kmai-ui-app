import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/services/auth';
import { toast } from 'sonner';

const SSOCallback: React.FC = () => {
  const navigate = useNavigate();
  const { setUser, setError } = useAuthStore();

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // Simulate fetching user data from SSO provider
        const userData = await new Promise<{ id: string; email: string; name: string; avatar: string }>((resolve) =>
          setTimeout(
            () =>
              resolve({
                id: '1',
                email: 'demo@example.com',
                name: 'Demo User',
                avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=demo@example.com',
              }),
            1000
          )
        );

        // Update the authentication state
        setUser(userData);

        // Redirect to the intended page or home
        navigate('/', { replace: true });
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred';
        setError(errorMessage);
        toast.error(errorMessage);
        navigate('/login', { replace: true });
      }
    };

    handleCallback();
  }, [navigate, setUser, setError]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h2 className="text-xl font-semibold">Processing SSO Login...</h2>
        <div className="mt-4 animate-spin h-8 w-8 border-4 border-blue-500 rounded-full border-t-transparent mx-auto"></div>
      </div>
    </div>
  );
};

export default SSOCallback;
