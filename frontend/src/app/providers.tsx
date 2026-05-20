"use client";

import { ReactNode } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { SolanaWalletProvider } from "@/lib/wallet/WalletProvider";
import { AuthSessionBootstrap } from "@/app/AuthSessionBootstrap";

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 30_000 } },
});

export function Providers({ children }: { children: ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      <SolanaWalletProvider>
        <AuthSessionBootstrap />
        {children}
      </SolanaWalletProvider>
    </QueryClientProvider>
  );
}
