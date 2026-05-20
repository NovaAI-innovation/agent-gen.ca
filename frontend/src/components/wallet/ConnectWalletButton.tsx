"use client";

import { useEffect, useSyncExternalStore } from "react";
import { useWallet } from "@solana/wallet-adapter-react";
import { WalletMultiButton } from "@solana/wallet-adapter-react-ui";
import { useAuthStore } from "@/store/authStore";
import { api } from "@/lib/api";

interface ChallengeResponse {
  challenge_id: string;
  nonce: string;
  message: string;
}

export function ConnectWalletButton() {
  const mounted = useSyncExternalStore(
    () => () => undefined,
    () => true,
    () => false
  );
  const { publicKey, signMessage, connected, disconnecting } = useWallet();
  const { token, setToken, fetchMe, logout } = useAuthStore();

  useEffect(() => {
    if (disconnecting) {
      void logout({ remote: true });
    }
  }, [disconnecting, logout]);

  useEffect(() => {
    if (!connected || !publicKey || !signMessage || token) return;

    const authenticate = async () => {
      try {
        const wallet = publicKey.toBase58();

        const { data } = await api.get<ChallengeResponse>("/auth/challenge", {
          params: { wallet },
        });

        // Validate message before signing to prevent signing tampered content.
        if (
          !data.message.includes(wallet) ||
          !data.message.includes(data.nonce) ||
          !data.message.includes("wants you to sign in with your Solana account")
        ) {
          throw new Error("Challenge message failed integrity check");
        }

        const message = new TextEncoder().encode(data.message);
        const signature = await signMessage(message);
        const signatureBase64 = Buffer.from(signature).toString("base64");

        const res = await api.post("/auth/verify", {
          wallet,
          challenge_id: data.challenge_id,
          nonce: data.nonce,
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

  if (!mounted) {
    return (
      <button
        type="button"
        className="wallet-adapter-button wallet-adapter-button-trigger"
        disabled
        aria-hidden="true"
      >
        Select Wallet
      </button>
    );
  }

  return <WalletMultiButton className="wallet-trigger" />;
}
