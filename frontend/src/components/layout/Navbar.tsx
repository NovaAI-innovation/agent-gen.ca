"use client";

import Link from "next/link";
import { useState } from "react";
import { usePathname } from "next/navigation";
import { ConnectWalletButton } from "@/components/wallet/ConnectWalletButton";
import { useAuthStore } from "@/store/authStore";
import { Button } from "@/components/ui/Button";
import { cn } from "@/lib/cn";
import { Menu, Plus, X } from "lucide-react";

const DISCOVER_LINKS = [
  { href: "/marketplace", label: "Marketplace" },
  { href: "/mcp-servers", label: "MCP Servers" },
  { href: "/agent-skills", label: "Skills" },
  { href: "/agents", label: "Agents" },
  { href: "/packs", label: "Packs" },
];

const CREATOR_LINKS = [
  { href: "/publish", label: "Publish" },
  { href: "/dashboard", label: "Dashboard" },
];

function NavLink({ href, label, active }: { href: string; label: string; active: boolean }) {
  return (
    <Link
      href={href}
      className={cn(
        "rounded-lg px-3 py-1.5 text-sm transition-all duration-200",
        active
          ? "bg-action-primary/15 text-primary border border-action-primary/40"
          : "text-text-secondary hover:bg-surface-muted hover:text-text-primary"
      )}
    >
      {label}
    </Link>
  );
}

export function Navbar() {
  const pathname = usePathname();
  const { user } = useAuthStore();
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="fixed inset-x-0 top-0 z-50 px-4 pt-4 sm:px-6">
      <div className="mx-auto max-w-7xl rounded-2xl border border-border-subtle bg-surface-elevated/80 px-4 py-3 backdrop-blur-md">
        <div className="flex items-center justify-between gap-4">
          <Link href="/" className="flex items-center gap-3">
            <div className="flex items-baseline gap-1.5 font-mono">
              <span className="text-sm font-bold tracking-[0.18em] text-text-secondary">AGENT</span>
              <span className="neon-text text-sm font-bold tracking-[0.18em] text-action-primary">GEN</span>
              <span className="text-xs tracking-[0.16em] text-text-muted">.CA</span>
            </div>
            <span className="hidden rounded-full border border-border-subtle bg-surface-muted px-2 py-0.5 font-mono text-[10px] uppercase tracking-[0.16em] text-text-muted md:inline-flex">
              Mission Control
            </span>
          </Link>

          <div className="hidden min-w-0 flex-1 items-center justify-between gap-5 lg:flex">
            <div className="flex items-center gap-1 rounded-xl border border-border-subtle bg-surface-muted p-1">
              {DISCOVER_LINKS.map(({ href, label }) => (
                <NavLink key={href} href={href} label={label} active={pathname === href || pathname.startsWith(`${href}/`)} />
              ))}
            </div>

            <div className="flex items-center gap-2">
              {CREATOR_LINKS.map(({ href, label }) => {
                if (href === "/dashboard" && !user) return null;
                return (
                  <NavLink
                    key={href}
                    href={href}
                    label={label}
                    active={pathname === href || pathname.startsWith(`${href}/`)}
                  />
                );
              })}
              <ConnectWalletButton />
            </div>
          </div>

          <div className="flex items-center gap-2 lg:hidden">
            {user ? (
              <Button asChild size="sm" variant="secondary" className="hidden sm:inline-flex">
                <Link href="/publish">
                  <Plus className="h-3.5 w-3.5" />
                  Publish
                </Link>
              </Button>
            ) : null}
            <ConnectWalletButton />
            <Button
              type="button"
              variant="secondary"
              size="icon"
              aria-label={menuOpen ? "Close menu" : "Open menu"}
              onClick={() => setMenuOpen((v) => !v)}
            >
              {menuOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
            </Button>
          </div>
        </div>

        {menuOpen ? (
          <div className="mt-3 space-y-3 border-t border-border-subtle pt-3 lg:hidden">
            <div>
              <p className="mb-2 font-mono text-[10px] uppercase tracking-[0.18em] text-text-muted">Discover</p>
              <div className="grid gap-1">
                {DISCOVER_LINKS.map(({ href, label }) => (
                  <NavLink key={href} href={href} label={label} active={pathname === href || pathname.startsWith(`${href}/`)} />
                ))}
              </div>
            </div>

            <div>
              <p className="mb-2 font-mono text-[10px] uppercase tracking-[0.18em] text-text-muted">Create</p>
              <div className="grid gap-1">
                {CREATOR_LINKS.map(({ href, label }) => {
                  if (href === "/dashboard" && !user) return null;
                  return (
                    <NavLink
                      key={href}
                      href={href}
                      label={label}
                      active={pathname === href || pathname.startsWith(`${href}/`)}
                    />
                  );
                })}
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </header>
  );
}
