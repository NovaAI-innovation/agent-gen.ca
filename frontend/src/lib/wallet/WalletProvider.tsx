"use client";

import { FC, ReactNode } from "react";
import { ConnectionProvider, WalletProvider } from "@solana/wallet-adapter-react";
import { getSolanaRuntimeConfig } from "@/lib/solana/config";

interface Props {
  children: ReactNode;
}

/**
 * SolanaWalletProvider uses Wallet Standard, which automatically detects
 * any installed wallet extension (Phantom, Solflare, Backpack, etc.)
 * without requiring explicit adapter packages.
 *
 * autoConnect is false — wallet connection and app sign-in are separate steps.
 */
export const SolanaWalletProvider: FC<Props> = ({ children }) => {
  const config = getSolanaRuntimeConfig();

  return (
    <ConnectionProvider endpoint={config.rpcHttp}>
      <WalletProvider wallets={[]} autoConnect={false}>
        {children}
      </WalletProvider>
    </ConnectionProvider>
  );
};