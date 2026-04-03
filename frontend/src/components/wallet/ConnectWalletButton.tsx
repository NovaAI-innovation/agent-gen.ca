"use client";

import { useEffect } from "react";
import { useWallet } from "@solana/wallet-adapter-react";
import { WalletMultiButton } from "@solana/wallet-adapter-react-ui";
import { useAuthStore } from "@/store/authStore";
import { api } from "@/lib/api";

export function ConnectWalletButton() {
  const { publicKey, signMessage, connected, disconnecting } = useWallet();
  const { token, setToken, fetchMe, logout } = useAuthStore();

  useEffect(() => {
    if (disconnecting) {
      logout();
    }
  }, [disconnecting, logout]);

  useEffect(() => {
    if (!connected || !publicKey || !signMessage || token) return;

    const authenticate = async () => {
      try {
        const wallet = publicKey.toBase58();

        // 1. Get challenge nonce
        const { data } = await api.get(`/auth/challenge?wallet=${wallet}`);
        const message = new TextEncoder().encode(data.message);

        // 2. Sign with Phantom
        const signature = await signMessage(message);
        const signatureBase64 = Buffer.from(signature).toString("base64");

        // 3. Verify and get JWT
        const res = await api.post("/auth/verify", {
          wallet,
          signature: signatureBase64,
        });

        setToken(res.data.access_token);
        await fetchMe();
      } catch (err) {
        console.error("Wallet auth failed:", err);
      }
    };

    authenticate();
  }, [connected, publicKey, signMessage, token, setToken, fetchMe]);

  return <WalletMultiButton className="wallet-trigger" />;
}
