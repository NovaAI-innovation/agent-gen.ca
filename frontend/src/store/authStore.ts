import { create } from "zustand";
import { api } from "@/lib/api";
import { setAccessToken } from "@/lib/authToken";

interface User {
  id: string;
  wallet_address: string;
  username: string | null;
  bio: string | null;
  avatar_url: string | null;
  reputation_score: number;
  is_verified: boolean;
  // Creator profile (IDN-005)
  handle?: string | null;
  display_name?: string | null;
  support_link?: string | null;
  creator_status?: "none" | "pending" | "approved" | "rejected";
}

interface AuthState {
  token: string | null;
  user: User | null;
  setToken: (token: string | null) => void;
  setUser: (user: User) => void;
  logout: (options?: { remote?: boolean }) => Promise<void>;
  fetchMe: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()((set, get) => ({
  token: null,
  user: null,
  setToken: (token) => {
    setAccessToken(token);
    set((state) => ({
      token,
      // Clear stale profile whenever the auth token changes.
      user: token === state.token ? state.user : null,
    }));
  },
  setUser: (user) => set({ user }),
  logout: async (options) => {
    const shouldRevokeSession = options?.remote ?? false;
    if (shouldRevokeSession && get().token) {
      try {
        await api.post("/auth/logout");
      } catch {
        // Best effort session revocation; local logout still clears auth state.
      }
    }

    setAccessToken(null);
    set({ token: null, user: null });
  },
  fetchMe: async () => {
    try {
      const res = await api.get("/users/me");
      set({ user: res.data });
    } catch {
      await get().logout();
    }
  },
}));
