export interface SolanaRuntimeConfig {
  cluster: "localnet" | "devnet" | "mainnet-beta";
  rpcHttp: string;
  rpcWs: string;
  rpcFallback: string[];
  usdcMint: string;
  platformFeeBps: number;
}

function readFallbackEndpoints(): string[] {
  const raw = process.env.NEXT_PUBLIC_SOLANA_RPC_FALLBACK ?? "";
  return raw
    .split(",")
    .map((part) => part.trim())
    .filter(Boolean);
}

export function getSolanaRuntimeConfig(): SolanaRuntimeConfig {
  const cluster = (process.env.NEXT_PUBLIC_SOLANA_CLUSTER ?? "mainnet-beta") as SolanaRuntimeConfig["cluster"];
  return {
    cluster,
    rpcHttp: process.env.NEXT_PUBLIC_SOLANA_RPC_HTTP ?? "https://api.mainnet-beta.solana.com",
    rpcWs: process.env.NEXT_PUBLIC_SOLANA_RPC_WS ?? "wss://api.mainnet-beta.solana.com",
    rpcFallback: readFallbackEndpoints(),
    usdcMint: process.env.NEXT_PUBLIC_USDC_MINT ?? "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    platformFeeBps: Number(process.env.NEXT_PUBLIC_PLATFORM_FEE_BPS ?? 250),
  };
}
