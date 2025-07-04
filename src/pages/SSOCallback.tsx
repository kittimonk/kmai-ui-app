import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/services/auth';
import { toast } from 'sonner';

const SSOCallback = () => {
  const navigate = useNavigate();
  const { setUser } = useAuthStore();

  useEffect(() => {
    const fetchUser = async () => {
      try {
        // Replace '/protected' with your actual backend endpoint
        const response = await fetch('/protected', {
          credentials: 'include',
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        if (data && data.user) {
          const { id, email, name } = data.user;
          setUser({
            id,
            email,
            name,
            avatar: `https://api.dicebear.com/7.x/avataaars/svg?seed=${email}`,
          });
          toast.success(`Welcome, ${name}!`);
          navigate('/');
        } else {
          throw new Error('User data not found in response');
        }
      } catch (error) {
        console.error('SSOCallback error:', error);
        toast.error('SSO authentication failed');
        navigate('/login');
      }
    };

    fetchUser();
  }, [navigate, setUser]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <p className="text-lg font-semibold">Authenticating...</p>
    </div>
  );
};

export default SSOCallback;
