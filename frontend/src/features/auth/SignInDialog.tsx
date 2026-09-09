"use client";

import { useCallback, useState } from "react";
import type { WalletName } from "@solana/wallet-adapter-base";
import { useWallet } from "@solana/wallet-adapter-react";
import { useAuthStore } from "@/store/authStore";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";

interface ChallengeResponse {
  challenge_id: string;
  nonce: string;
  domain: string;
  uri: string;
  chain_id: string;
  issued_at: string;
  expires_at: string;
  message: string;
}

interface Props {
  open: boolean;
  onClose: () => void;
}

export function SignInDialog({ open, onClose }: Props) {
  const {
    wallets,
    select,
    connect,
    publicKey,
    connected,
    connecting,
    signMessage,
  } = useWallet();
  const { token, setToken, fetchMe } = useAuthStore();
  const [signingIn, setSigningIn] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState<"connect" | "sign-in">(
    connected ? "sign-in" : "connect"
  );

  const alreadySignedIn = !!token;

  const handleSelectWallet = useCallback(
    async (walletName: WalletName) => {
      setError(null);
      try {
        select(walletName);
        await connect();
        setStep("sign-in");
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to connect wallet");
      }
    },
    [select, connect]
  );

  const handleSignIn = useCallback(async () => {
    if (!publicKey || !signMessage || alreadySignedIn) return;
    setSigningIn(true);
    setError(null);

    try {
      const wallet = publicKey.toBase58();

      // 1. Get challenge
      const { data: challenge } = await api.get<ChallengeResponse>(
        "/auth/challenge",
        { params: { wallet } }
      );

      // 2. Integrity check before signing
      if (
        !challenge.message.includes(wallet) ||
        !challenge.message.includes(challenge.nonce)
      ) {
        throw new Error("Challenge message failed integrity check");
      }

      // 3. Sign message with wallet
      const messageBytes = new TextEncoder().encode(challenge.message);
      const signatureBytes = await signMessage(messageBytes);

      // 4. Submit SIWS verify with all independent fields
      const signatureBase64 = Buffer.from(signatureBytes).toString("base64");
      const res = await api.post("/auth/siws/verify", {
        wallet,
        challenge_id: challenge.challenge_id,
        nonce: challenge.nonce,
        signature: signatureBase64,
        domain: challenge.domain,
        uri: challenge.uri,
        chain_id: challenge.chain_id,
        issued_at: challenge.issued_at,
      });

      setToken(res.data.access_token);
      await fetchMe();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sign-in failed");
    } finally {
      setSigningIn(false);
    }
  }, [publicKey, signMessage, alreadySignedIn, setToken, fetchMe, onClose]);

  const detectedWallets = wallets.filter(
    (w) => w.readyState === "Installed" || w.readyState === "Loadable"
  );

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Dialog */}
      <div className="relative z-10 w-full max-w-md rounded-2xl border border-border-subtle bg-surface-elevated p-6 shadow-2xl">
        <div className="mb-5 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-text-primary">
            {step === "connect" ? "Connect Wallet" : "Sign In"}
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1 text-text-muted transition-colors hover:bg-surface-muted hover:text-text-primary"
            aria-label="Close"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M15 5L5 15M5 5l10 10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
            </svg>
          </button>
        </div>

        {error && (
          <Alert variant="danger" className="mb-4">
            {error}
          </Alert>
        )}

        {alreadySignedIn ? (
          <div className="space-y-4">
            <Alert variant="success">You are already signed in.</Alert>
            <Button variant="secondary" onClick={onClose} className="w-full">
              Close
            </Button>
          </div>
        ) : step === "connect" ? (
          <div className="space-y-3">
            <p className="text-sm text-text-secondary">
              Select a Solana wallet to connect with.
            </p>
            {detectedWallets.length === 0 ? (
              <p className="text-sm text-status-warning">
                No Solana wallets detected. Install Phantom or Solflare to
                continue.
              </p>
            ) : (
              <div className="space-y-2">
                {detectedWallets.map((wallet) => (
                  <button
                    key={wallet.adapter.name}
                    type="button"
                    onClick={() => handleSelectWallet(wallet.adapter.name)}
                    disabled={connecting}
                    className="flex w-full items-center gap-3 rounded-xl border border-border-subtle bg-surface-muted px-4 py-3 text-left text-sm text-text-primary transition-all hover:border-action-primary/40 hover:bg-surface-elevated disabled:opacity-50"
                  >
                    {wallet.adapter.icon && (
                      <img
                        src={wallet.adapter.icon}
                        alt=""
                        className="h-6 w-6 rounded-full"
                      />
                    )}
                    <span className="flex-1 font-medium">
                      {wallet.adapter.name}
                    </span>
                    {connecting && (
                      <span className="text-xs text-text-muted">
                        Connecting...
                      </span>
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            <Alert variant="info">
              Sign-in is{" "}
              <strong className="font-semibold">free</strong>. It proves you own
              this wallet and creates a session on{" "}
              <strong className="font-semibold">
                agent-gen.ca (Solana mainnet)
              </strong>
              .
            </Alert>

            <div className="rounded-xl border border-border-subtle bg-surface-muted p-3 text-sm">
              <div className="flex items-center gap-2">
                <span className="text-text-muted">Wallet:</span>
                <span className="font-mono text-text-primary">
                  {publicKey?.toBase58().slice(0, 4)}...
                  {publicKey?.toBase58().slice(-4)}
                </span>
              </div>
              <div className="mt-1 flex items-center gap-2">
                <span className="text-text-muted">Network:</span>
                <span className="text-text-primary">Solana mainnet</span>
              </div>
            </div>

            <Button
              onClick={handleSignIn}
              loading={signingIn}
              className="w-full"
            >
              Sign In with Solana
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}