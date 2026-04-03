"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ConnectWalletButton } from "@/components/wallet/ConnectWalletButton";
import { useAuthStore } from "@/store/authStore";
import { Plus } from "lucide-react";

const NAV_LINKS = [
  { href: "/marketplace", label: "All" },
  { href: "/mcp-servers", label: "MCP Servers" },
  { href: "/agent-skills", label: "Skills" },
  { href: "/agents", label: "Agents" },
  { href: "/packs", label: "Packs" },
];

export function Navbar() {
  const { user } = useAuthStore();
  const pathname = usePathname();

  return (
    <header className="fixed inset-x-0 top-0 z-50 flex justify-center px-4 pt-4">
      <nav className="glass relative flex w-full max-w-5xl items-center justify-between gap-6 overflow-hidden rounded-2xl px-5 py-3">
        <div
          className="pointer-events-none absolute inset-x-0 top-0 h-px"
          style={{
            background:
              "linear-gradient(90deg, transparent 0%, hsl(var(--primary) / 0.65) 50%, transparent 100%)",
          }}
        />

        <Link href="/" className="flex flex-shrink-0 items-center gap-2">
          <div className="flex items-baseline gap-1.5">
            <span className="font-mono text-sm font-bold tracking-widest text-foreground/80">AGENT</span>
            <span
              className="font-mono text-sm font-bold tracking-widest neon-text"
              style={{ color: "hsl(var(--primary))" }}
            >
              GEN
            </span>
            <span className="font-mono text-xs text-muted-foreground">.CA</span>
          </div>
          <span className="hidden rounded-full border border-primary/30 bg-primary/10 px-2 py-0.5 font-mono text-[9px] uppercase tracking-[0.16em] text-primary sm:inline-flex">
            Marketplace
          </span>
        </Link>

        <div className="hidden items-center gap-1 md:flex">
          {NAV_LINKS.map(({ href, label }) => {
            const active = pathname === href || (href !== "/" && pathname.startsWith(href));
            return (
              <Link
                key={href}
                href={href}
                className={`rounded-lg px-3 py-1.5 text-sm font-medium transition-all duration-200 ${
                  active
                    ? "bg-primary/10 text-primary shadow-[inset_0_-1px_0_hsl(var(--primary)_/_0.55)]"
                    : "text-muted-foreground hover:bg-white/5 hover:text-foreground"
                }`}
              >
                {label}
              </Link>
            );
          })}
        </div>

        <div className="flex flex-shrink-0 items-center gap-2">
          {user && (
            <>
              <Link
                href="/publish"
                className="hidden items-center gap-1.5 rounded-xl border border-primary/40 bg-primary/10 px-3 py-1.5 text-sm font-semibold text-primary transition-all duration-200 hover:border-primary/70 hover:bg-primary/20 sm:flex"
              >
                <Plus className="h-3.5 w-3.5" />
                Publish
              </Link>
              <Link
                href="/dashboard"
                className="hidden rounded-lg px-3 py-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground sm:block"
              >
                Dashboard
              </Link>
            </>
          )}
          <ConnectWalletButton />
        </div>
      </nav>
    </header>
  );
}
