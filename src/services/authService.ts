import { toast } from "sonner";

interface User {
  email: string;
  name: string;
  username: string;
}

const mockUser = {
  email: "demo@example.com",
  name: "Demo User",
  username: "demouser"
};

const demoCredentials = {
  email: "demo@example.com",
  password: "password"
};

const initialState = {
  isAuthenticated: true,
  user: mockUser,
  token: "mock-token-for-testing"
};

let currentState = initialState;

const listeners: (() => void)[] = [];

const getAuthState = () => currentState;

const updateAuthState = (newState: Partial<typeof initialState>): void => {
  currentState = { ...currentState, ...newState };
  listeners.forEach(listener => listener());
};

const subscribe = (listener: () => void): (() => void) => {
  listeners.push(listener);
  return () => {
    const index = listeners.indexOf(listener);
    if (index > -1) {
      listeners.splice(index, 1);
    }
  };
};

const login = (): void => {
  toast.success("Test mode: Already logged in");
};

const loginWithEmailPassword = async (email: string, password: string): Promise<boolean> => {
  await new Promise(resolve => setTimeout(resolve, 1000));
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

const handleCallback = async (): Promise<boolean> => {
  toast.success("Authentication successful (Test Mode)");
  return true;
};

const logout = (): void => {
  toast.info("Logout clicked (Test Mode - Still authenticated)");
};

const getAuthHeader = (): Record<string, string> => {
  return { Authorization: `Bearer ${currentState.token}` };
};

const isAuthenticated = (): boolean => {
  return true;
};

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
