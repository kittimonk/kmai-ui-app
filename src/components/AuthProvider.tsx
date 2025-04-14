import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/authService';

interface User {
  email: string;
  name: string;
  username: string;
}

interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  loading: boolean;
  login: () => void;
  loginWithEmailPassword: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// For testing - mock user
const mockUser = {
  email: "demo@example.com",
  name: "Demo User",
  username: "demouser"
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, setState] = useState({
    isAuthenticated: true, // For testing, always authenticated
    user: mockUser,
    loading: false,
  });

  useEffect(() => {
    // In a real app, we'd check for existing authentication here
    // For demo purposes, we're always authenticated
  }, []);

  const value = {
    isAuthenticated: state.isAuthenticated,
    user: state.user,
    loading: state.loading,
    login: authService.login,
    loginWithEmailPassword: async (email: string, password: string) => {
      setState(prev => ({ ...prev, loading: true }));
      try {
        // In a real app, we'd make an API call here
        // For demo, we'll just check against our mock credentials
        const success = await authService.loginWithEmailPassword(email, password);
        if (success) {
          setState({
            isAuthenticated: true,
            user: mockUser,
            loading: false,
          });
        } else {
          setState(prev => ({ ...prev, loading: false }));
        }
        return success;
      } catch (error) {
        setState(prev => ({ ...prev, loading: false }));
        return false;
      }
    },
    logout: () => {
      // In a real app, we'd make an API call here
      // For demo, we'll just update our local state
      authService.logout();
      // In a real app, we would set isAuthenticated to false
      // For demo, we keep it true for easy testing
    },
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
