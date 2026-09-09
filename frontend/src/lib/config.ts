/**
 * Central frontend environment contract.
 *
 * All `NEXT_PUBLIC_*` variables are resolved at build time by Next.js.
 * Non-public variables are available only in server components and API routes.
 *
 * This module validates and exports a single typed config object.
 * Import from here instead of reading `process.env` directly.
 */

// ── Types ────────────────────────────────────────────────────────────────

export type Cluster = "localnet" | "devnet" | "mainnet-beta";

export interface AppConfig {
  /** Backend API base URL. Resolved for browser vs SSR contexts. */
  apiUrl: string;

  /** Solana cluster identifier. */
  cluster: Cluster;

  /** Primary Solana JSON-RPC HTTP endpoint. */
  rpcHttp: string;

  /** Primary Solana JSON-RPC WebSocket endpoint. */
  rpcWs: string;

  /** Fallback Solana RPC endpoints (comma-separated in env). */
  rpcFallback: string[];

  /** USDC token mint address. */
  usdcMint: string;

  /** Platform fee in basis points (e.g. 250 = 2.5%). */
  platformFeeBps: number;

  /** Current environment: development or production. */
  environment: "development" | "production";
}

// ── Validation ───────────────────────────────────────────────────────────

const VALID_CLUSTERS: ReadonlySet<string> = new Set([
  "localnet",
  "devnet",
  "mainnet-beta",
]);

function readEnv(key: string, fallback?: string): string {
  const value = process.env[key];
  if (value !== undefined && value.trim() !== "") return value.trim();
  if (fallback !== undefined) return fallback;
  throw new Error(`Missing required environment variable: ${key}`);
}

function readOptionalEnv(key: string): string | undefined {
  const value = process.env[key];
  return value !== undefined && value.trim() !== "" ? value.trim() : undefined;
}

function parseCommaList(raw: string | undefined): string[] {
  if (!raw) return [];
  return raw
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
}

function isProduction(): boolean {
  const env = (process.env.ENVIRONMENT ?? "development").toLowerCase();
  return env === "production" || env === "prod";
}

function isLoopback(hostname: string): boolean {
  return (
    hostname === "localhost" ||
    hostname === "127.0.0.1" ||
    hostname === "::1"
  );
}

function extractHostname(url: string): string {
  try {
    return new URL(url).hostname;
  } catch {
    return "";
  }
}

// ── Browser API URL resolution ───────────────────────────────────────────

function resolveBrowserApiBaseUrl(configuredUrl?: string): string {
  if (typeof window === "undefined") {
    return configuredUrl ?? "http://localhost:8000";
  }

  const currentUrl = new URL(window.location.origin);

  if (!configuredUrl) {
    if (isLoopback(currentUrl.hostname)) {
      return "http://localhost:8000";
    }

    if (currentUrl.protocol === "https:") {
      return "/api";
    }

    return `${currentUrl.protocol}//${currentUrl.hostname}:8000`;
  }

  const normalizedUrl = new URL(configuredUrl, currentUrl);

  if (
    isLoopback(normalizedUrl.hostname) &&
    !isLoopback(currentUrl.hostname)
  ) {
    if (currentUrl.protocol === "https:") {
      return "/api";
    }

    const path =
      normalizedUrl.pathname === "/"
        ? ""
        : normalizedUrl.pathname.replace(/\/$/, "");
    const port = normalizedUrl.port ? `:${normalizedUrl.port}` : "";
    return `${normalizedUrl.protocol}//${currentUrl.hostname}${port}${path}`;
  }

  if (
    currentUrl.protocol === "https:" &&
    normalizedUrl.protocol === "http:" &&
    normalizedUrl.origin !== currentUrl.origin
  ) {
    return "/api";
  }

  return configuredUrl;
}

// ── Config builder ───────────────────────────────────────────────────────

let _cached: AppConfig | null = null;

export function getAppConfig(): AppConfig {
  if (_cached) return _cached;

  const environment: AppConfig["environment"] = isProduction()
    ? "production"
    : "development";

  const apiUrl = resolveBrowserApiBaseUrl(
    readOptionalEnv("NEXT_PUBLIC_API_URL")
  );

  const cluster = (readOptionalEnv("NEXT_PUBLIC_SOLANA_CLUSTER") ??
    "mainnet-beta") as Cluster;

  if (!VALID_CLUSTERS.has(cluster)) {
    throw new Error(
      `NEXT_PUBLIC_SOLANA_CLUSTER must be one of [${[...VALID_CLUSTERS].join(", ")}], got '${cluster}'.`
    );
  }

  const rpcHttp =
    readOptionalEnv("NEXT_PUBLIC_SOLANA_RPC_HTTP") ??
    "https://api.mainnet-beta.solana.com";

  const rpcWs =
    readOptionalEnv("NEXT_PUBLIC_SOLANA_RPC_WS") ??
    "wss://api.mainnet-beta.solana.com";

  const rpcFallback = parseCommaList(
    readOptionalEnv("NEXT_PUBLIC_SOLANA_RPC_FALLBACK")
  );

  const usdcMint =
    readOptionalEnv("NEXT_PUBLIC_USDC_MINT") ??
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v";

  const platformFeeBps = Number(
    readOptionalEnv("NEXT_PUBLIC_PLATFORM_FEE_BPS") ?? "250"
  );

  if (Number.isNaN(platformFeeBps) || platformFeeBps < 0 || platformFeeBps > 10_000) {
    throw new Error(
      `NEXT_PUBLIC_PLATFORM_FEE_BPS must be an integer between 0 and 10000.`
    );
  }

  // ── Production guards ────────────────────────────────────────────────

  if (environment === "production") {
    const errors: string[] = [];

    if (cluster === "localnet") {
      errors.push(
        "NEXT_PUBLIC_SOLANA_CLUSTER must not be 'localnet' in production."
      );
    }

    if (isLoopback(extractHostname(rpcHttp))) {
      errors.push(
        "NEXT_PUBLIC_SOLANA_RPC_HTTP must not point to a loopback address in production."
      );
    }

    if (errors.length > 0) {
      throw new Error(
        "Production configuration errors:\n  - " + errors.join("\n  - ")
      );
    }
  }

  _cached = {
    apiUrl,
    cluster,
    rpcHttp,
    rpcWs,
    rpcFallback,
    usdcMint,
    platformFeeBps,
    environment,
  };

  return _cached;
}

/**
 * Reset cached config. Only for testing.
 */
export function resetConfigCache(): void {
  _cached = null;
}
