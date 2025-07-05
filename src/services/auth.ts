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
  setLoading: (loading: boolean) => void;
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: true,
      error: null,

      login: async (email, password) => {
        set({ isLoading: true, error: null });
        try {
          await new Promise((r) => setTimeout(r, 1000));
          if (email === 'demo@example.com' && password === 'password') {
            set({
              user: {
                id: '1',
                email,
                name: 'Demo User',
                avatar: `https://api.dicebear.com/7.x/avataaars/svg?seed=${email}`,
              },
              isAuthenticated: true,
              isLoading: false,
            });
          } else {
            throw new Error('Invalid credentials');
          }
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Login error',
            isLoading: false,
          });
        }
      },

      register: async (name, email, password) => {
        set({ isLoading: true, error: null });
        try {
          await new Promise((r) => setTimeout(r, 1000));
          set({
            user: {
              id: '1',
              email,
              name,
              avatar: `https://api.dicebear.com/7.x/avataaars/svg?seed=${email}`,
            },
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Register error',
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

      setUser: (user) => {
        set({
          user,
          isAuthenticated: true,
          isLoading: false,
        });
      },

      setLoading: (isLoading) => set({ isLoading }),
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => localStorage),
      version: 1,
    }
  )
);

// ✅ Make checkAuthStatus return a Promise
export const checkAuthStatus = async (): Promise<void> => {
  const store = useAuthStore.getState();
  store.setLoading(true);

  try {
    const res = await fetch('/protected', {
      credentials: 'include',
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    console.log('✅ checkAuthStatus ➜', data);

    if (data?.user) {
      const { sub, aud, jti } = data.user;
      useAuthStore.setState({
        user: { 
          id: sub || aud, 
          email: sub || 'user@company.com',
          name: sub || 'SSO User'
        },
        isAuthenticated: true,
        isLoading: false,
      });
    } else {
      useAuthStore.setState({ user: null, isAuthenticated: false, isLoading: false });
    }
  } catch (err) {
    console.error('checkAuthStatus failed:', err);
    useAuthStore.setState({ user: null, isAuthenticated: false, isLoading: false });
  }
};
