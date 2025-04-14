
import { toast } from "sonner";

interface User {
  email: string;
  name: string;
  username: string;
}

// Mock user for testing
const mockUser = {
  email: "demo@example.com",
  name: "Demo User",
  username: "demouser"
};

// Demo credentials
const demoCredentials = {
  email: "demo@example.com",
  password: "password"
};

// Initial auth state - for testing, always authenticated
const initialState = {
  isAuthenticated: true,
  user: mockUser,
  token: "mock-token-for-testing"
};

// Current auth state
let currentState = initialState;

// Listeners for state changes
const listeners: (() => void)[] = [];

// Get current auth state
const getAuthState = () => currentState;

// Update auth state and notify listeners
const updateAuthState = (newState: Partial<typeof initialState>): void => {
  currentState = { ...currentState, ...newState };
  listeners.forEach(listener => listener());
};

// Subscribe to auth state changes
const subscribe = (listener: () => void): (() => void) => {
  listeners.push(listener);
  return () => {
    const index = listeners.indexOf(listener);
    if (index > -1) {
      listeners.splice(index, 1);
    }
  };
};

// Login with SSO - for testing, just show a toast
const login = (): void => {
  toast.success("Test mode: Already logged in");
};

// Login with email and password
const loginWithEmailPassword = async (email: string, password: string): Promise<boolean> => {
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Check credentials (for demo)
  if (email === demoCredentials.email && password === demoCredentials.password) {
    toast.success("Login successful");
    updateAuthState({
      isAuthenticated: true,
      user: mockUser,
      token: "mock-token-for-testing"
    });
    return true;
  }
  
  toast.error("Invalid email or password");
  return false;
};

// Handle SSO callback - for testing, always successful
const handleCallback = async (): Promise<boolean> => {
  toast.success("Authentication successful (Test Mode)");
  return true;
};

// Logout - for testing, shows toast but doesn't change state
const logout = (): void => {
  toast.info("Logout clicked (Test Mode - Still authenticated)");
};

// Get auth header for API requests
const getAuthHeader = (): Record<string, string> => {
  return { Authorization: `Bearer ${currentState.token}` };
};

// Check if current user is authenticated - for testing, always true
const isAuthenticated = (): boolean => {
  return true;
};

// Get current user - for testing, always returns mock user
const getCurrentUser = (): User => {
  return mockUser;
};

export const authService = {
  getAuthState,
  subscribe,
  login,
  loginWithEmailPassword,
  handleCallback,
  logout,
  getAuthHeader,
  isAuthenticated,
  getCurrentUser,
};
