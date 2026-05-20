"use client";

import { useEffect, useRef } from "react";
import { useAuthStore } from "@/store/authStore";
import { refreshAccessToken } from "@/lib/api";

export function AuthSessionBootstrap() {
  const { token, user, setToken, fetchMe, logout } = useAuthStore();
  const initialized = useRef(false);

  useEffect(() => {
    if (initialized.current) return;
    initialized.current = true;

    const init = async () => {
      if (!token) {
        // No in-memory token — attempt silent restore from httpOnly refresh cookie.
        const newToken = await refreshAccessToken();
        if (newToken) {
          setToken(newToken);
          await fetchMe();
        }
      } else if (!user) {
        await fetchMe();
      }
    };

    void init();
    // Intentionally empty deps: runs once on mount to bootstrap auth state.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const onAuthLogout = () => void logout();
    window.addEventListener("auth:logout", onAuthLogout);
    return () => window.removeEventListener("auth:logout", onAuthLogout);
  }, [logout]);

  return null;
}
