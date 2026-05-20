import { getSolanaRuntimeConfig } from "./config";

export interface SolanaClientEndpoints {
  primaryHttp: string;
  primaryWs: string;
  fallbackHttp: string[];
}

export function getSolanaClientEndpoints(): SolanaClientEndpoints {
  const cfg = getSolanaRuntimeConfig();
  return {
    primaryHttp: cfg.rpcHttp,
    primaryWs: cfg.rpcWs,
    fallbackHttp: cfg.rpcFallback,
  };
}
