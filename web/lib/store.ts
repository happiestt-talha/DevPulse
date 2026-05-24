import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  github_username: string;
  display_name: string | null;
  avatar_url: string | null;
  email: string | null;
  level: number;
  total_xp: number;
  streak_current: number;
  streak_longest: number;
  developer_score: number;
  wakatime_connected: boolean;
  leetcode_connected: boolean;
}

interface AuthState {
  accessToken: string | null;
  user: User | null;
  setAccessToken: (token: string | null) => void;
  setUser: (user: User | null) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      user: null,
      setAccessToken: (token) => set({ accessToken: token }),
      setUser: (user) => set({ user }),
      logout: () => set({ accessToken: null, user: null }),
    }),
    {
      name: 'devpulse-auth',
      partialize: (state) => ({ accessToken: state.accessToken, user: state.user }),
    }
  )
);