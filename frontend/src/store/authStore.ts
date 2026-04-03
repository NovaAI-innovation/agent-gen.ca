import { create } from "zustand";
import { persist } from "zustand/middleware";
import { api } from "@/lib/api";

interface User {
  id: string;
  wallet_address: string;
  username: string | null;
  bio: string | null;
  avatar_url: string | null;
  reputation_score: number;
  is_verified: boolean;
}

interface AuthState {
  token: string | null;
  user: User | null;
  setToken: (token: string) => void;
  setUser: (user: User) => void;
  logout: () => void;
  fetchMe: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      setToken: (token) => {
        localStorage.setItem("access_token", token);
        set({ token });
      },
      setUser: (user) => set({ user }),
      logout: () => {
        localStorage.removeItem("access_token");
        set({ token: null, user: null });
      },
      fetchMe: async () => {
        try {
          const res = await api.get("/users/me");
          set({ user: res.data });
        } catch {
          get().logout();
        }
      },
    }),
    { name: "auth-storage", partialize: (s) => ({ token: s.token }) }
  )
);
