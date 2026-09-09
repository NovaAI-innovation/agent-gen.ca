/**
 * Solana runtime configuration.
 *
 * Re-exports the Solana-related subset of the central AppConfig.
 * Import from @/lib/config for the full config.
 */

import { getAppConfig, type Cluster } from "@/lib/config";

export interface SolanaRuntimeConfig {
  cluster: Cluster;
  rpcHttp: string;
  rpcWs: string;
  rpcFallback: string[];
  usdcMint: string;
  platformFeeBps: number;
}

/**
 * Returns the Solana subset of the application config.
 * Cached on first call — safe to use in render paths.
 */
export function getSolanaRuntimeConfig(): SolanaRuntimeConfig {
  const config = getAppConfig();
  return {
    cluster: config.cluster,
    rpcHttp: config.rpcHttp,
    rpcWs: config.rpcWs,
    rpcFallback: config.rpcFallback,
    usdcMint: config.usdcMint,
    platformFeeBps: config.platformFeeBps,
  };
}
