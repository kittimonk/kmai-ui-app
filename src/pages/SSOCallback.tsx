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
        const response = await fetch('/protected', { credentials: 'include' });
        if (!response.ok) throw new Error('Failed to fetch user info');

        const data = await response.json();

        if (data.user) {
          setUser({
            id: data.user.id,
            email: data.user.email,
            name: data.user.name,
            // You can generate avatar URL here if you want
          });
          toast.success(`Welcome, ${data.user.name}!`);
          navigate('/');
        } else {
          throw new Error('No user data returned');
        }
      } catch (error) {
        toast.error('SSO login failed. Please sign in again.');
        navigate('/login');
      }
    };
    fetchUser();
  }, [navigate, setUser]);

  return <div>Loading...</div>;
};

export default SSOCallback;
