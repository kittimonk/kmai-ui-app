import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '@/services/auth';

const Index = () => {
  const { isAuthenticated } = useAuthStore();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <Navigate to="/chat" replace />;
};

export default Index;