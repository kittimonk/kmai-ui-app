import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/services/auth';

const SSOCallback = () => {
  const navigate = useNavigate();
  const { setUser } = useAuthStore();

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await fetch("/protected");
        if (!response.ok) {
          throw new Error("Failed to fetch user information");
        }
        const data = await response.json();
        setUser(data.user);
        navigate("/");
      } catch (error) {
        console.error("Error during SSO callback:", error);
        navigate("/login"); // Redirect to login on error
      }
    };
    fetchUser();
  }, [navigate, setUser]);

  return <div>Loading...</div>;
};

export default SSOCallback;