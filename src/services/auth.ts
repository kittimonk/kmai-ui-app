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
  setUser: (user: User) => void; // Added setUser method
};

// Updated implementation
export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          // Simulate API call delay
          await new Promise((resolve) => setTimeout(resolve, 1000));
          
          // In a real app, validate credentials against a backend
          if (email === "demo@example.com" && password === "password") {
            set({
              user: {
                id: "1",
                email,
                name: "Demo User",
                avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=${email}",
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
          // Simulate API call delay
          await new Promise((resolve) => setTimeout(resolve, 1000));
          
          // In a real app, register the user with a backend
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
        set({ user: null, isAuthenticated: false });
      },
      setUser: (user: User) => {
        set({ user, isAuthenticated: true }); // Set user and mark as authenticated
      },
    }),
    {
      name: "auth-storage",
      storage: createJSONStorage(() => localStorage),
    }
  )
);