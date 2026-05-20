from __future__ import annotations

from dataclasses import dataclass

from .config import settings


@dataclass(frozen=True)
class SolanaConfig:
    cluster: str
    rpc_http: str
    rpc_ws: str
    rpc_fallback: tuple[str, ...]
    usdc_mint: str
    platform_fee_bps: int


def get_solana_config() -> SolanaConfig:
    fallback = tuple(
        endpoint.strip()
        for endpoint in (settings.SOLANA_RPC_FALLBACK or "").split(",")
        if endpoint.strip()
    )
    return SolanaConfig(
        cluster=settings.SOLANA_CLUSTER,
        rpc_http=settings.SOLANA_RPC_HTTP,
        rpc_ws=settings.SOLANA_RPC_WS,
        rpc_fallback=fallback,
        usdc_mint=settings.USDC_MINT,
        platform_fee_bps=settings.PLATFORM_FEE_BPS,
    )
