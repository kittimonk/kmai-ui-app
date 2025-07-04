import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
}

export type AuthState = {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  setUser: (user: User) => void;
  clearError: () => void;
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          await new Promise((resolve) => setTimeout(resolve, 1000));
          if (email === "demo@example.com" && password === "password") {
            set({
              user: {
                id: "1",
                email,
                name: "Demo User",
                avatar: `https://api.dicebear.com/7.x/avataaars/svg?seed=${email}`,
              },
              isAuthenticated: true,
              isLoading: false,
            });
          } else {
            throw new Error("Invalid credentials");
          }
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : "An unknown error occurred",
            isLoading: false,
          });
        }
      },
      register: async (name: string, email: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          await new Promise((resolve) => setTimeout(resolve, 1000));
          set({
            user: {
              id: "1",
              email,
              name,
              avatar: `https://api.dicebear.com/7.x/avataaars/svg?seed=${email}`,
            },
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : "An unknown error occurred",
            isLoading: false,
          });
        }
      },
      logout: () => {
        fetch('/logout', { method: 'GET', credentials: 'include' })
          .then(() => {
            set({ user: null, isAuthenticated: false });
          })
          .catch(() => {
            set({ user: null, isAuthenticated: false });
          });
      },
      setUser: (user: User) => {
        set({ user, isAuthenticated: true });
      },
      clearError: () => set({ error: null }),
    }),
    {
      name: "auth-storage",
      storage: createJSONStorage(() => localStorage),
    }
  )
);

export const checkAuthStatus = async () => {
  try {
    const response = await fetch('/api/auth/status', {
      credentials: 'include'
    });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const data = await response.json();
    if (data.isAuthenticated && data.user) {
      useAuthStore.getState().setUser({
        id: data.user.id,
        email: data.user.email,
        name: data.user.name,
        avatar: `https://api.dicebear.com/7.x/avataaars/svg?seed=${data.user.email}`
      });
    } else {
      useAuthStore.setState({ user: null, isAuthenticated: false });
    }
  } catch (error) {
    console.error('Failed to check auth status:', error);
  }
};
