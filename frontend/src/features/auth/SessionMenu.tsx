"use client";

import { useWallet } from "@solana/wallet-adapter-react";
import { useAuthStore } from "@/store/authStore";

export function SessionMenu() {
  const { user, logout } = useAuthStore();
  const { publicKey, disconnect } = useWallet();

  if (!user) return null;

  const displayName =
    user.username ?? `${user.wallet_address.slice(0, 4)}...${user.wallet_address.slice(-4)}`;

  const handleLogout = async () => {
    await logout({ remote: true });
    await disconnect();
  };

  return (
    <div className="relative group">
      <button
        type="button"
        className="flex items-center gap-2 rounded-lg border border-border-subtle bg-surface-muted px-3 py-1.5 text-sm text-text-primary transition-all duration-200 hover:border-action-primary/40 hover:bg-surface-elevated"
      >
        <span className="flex h-5 w-5 items-center justify-center rounded-full bg-action-primary/20 text-[10px] font-bold text-action-primary">
          {displayName.charAt(0).toUpperCase()}
        </span>
        <span className="hidden sm:inline">{displayName}</span>
      </button>

      <div className="absolute right-0 top-full z-50 mt-1 hidden w-56 overflow-hidden rounded-xl border border-border-subtle bg-surface-elevated shadow-lg group-hover:block">
        <div className="border-b border-border-subtle px-4 py-3">
          <p className="text-xs text-text-muted">Signed in as</p>
          <p className="truncate text-sm font-medium text-text-primary">
            {displayName}
          </p>
        </div>
        <button
          type="button"
          onClick={handleLogout}
          className="flex w-full items-center gap-2 px-4 py-2.5 text-left text-sm text-status-danger transition-colors hover:bg-surface-muted"
        >
          Sign Out
        </button>
      </div>
    </div>
  );
}