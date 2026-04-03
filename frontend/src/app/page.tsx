import Link from "next/link";
import { Navbar } from "@/components/layout/Navbar";
import {
  Activity,
  ArrowRight,
  ArrowUpRight,
  Bot,
  Download,
  Package,
  Server,
  ShieldCheck,
  Sparkles,
  Star,
  Workflow,
  Zap,
} from "lucide-react";

const CATEGORIES = [
  {
    icon: Server,
    label: "MCP Servers",
    description: "Model Context Protocol packages",
    href: "/mcp-servers",
    glowClass: "glow-mcp",
    colorVar: "var(--accent-mcp)",
    bg: "hsl(183 100% 50% / 0.08)",
    border: "hsl(183 100% 50% / 0.2)",
    count: "140+",
  },
  {
    icon: Zap,
    label: "Agent Skills",
    description: "Reusable tools for AI agents",
    href: "/agent-skills",
    glowClass: "glow-skill",
    colorVar: "hsl(var(--accent-skill))",
    bg: "hsl(38 95% 55% / 0.08)",
    border: "hsl(38 95% 55% / 0.2)",
    count: "320+",
  },
  {
    icon: Bot,
    label: "Custom Agents",
    description: "Full agent configs and personalities",
    href: "/agents",
    glowClass: "glow-agent",
    colorVar: "hsl(var(--accent-agent))",
    bg: "hsl(142 75% 50% / 0.08)",
    border: "hsl(142 75% 50% / 0.2)",
    count: "85+",
  },
  {
    icon: Package,
    label: "Packs",
    description: "Curated bundles of marketplace items",
    href: "/packs",
    glowClass: "glow-pack",
    colorVar: "hsl(var(--accent-pack))",
    bg: "hsl(270 85% 65% / 0.08)",
    border: "hsl(270 85% 65% / 0.2)",
    count: "40+",
  },
];

const STATS = [
  { label: "Listings", value: "500+" },
  { label: "Contributors", value: "1.2K" },
  { label: "Downloads", value: "48K" },
  { label: "Avg Rating", value: "4.8" },
];

const LIVE_FEED = [
  { label: "New listings", value: "+24", detail: "last 7 days" },
  { label: "Verified creators", value: "312", detail: "wallet linked" },
  { label: "SOL volume", value: "8.4k", detail: "rolling 30d" },
  { label: "Avg install time", value: "48s", detail: "one-click flow" },
];

const FEATURED_BUILDS = [
  {
    title: "Prompt Firewall",
    type: "Security Skill",
    description: "Policy-aware runtime checks for risky tool calls and prompt injection vectors.",
    installs: "2.9k installs",
    rating: "4.9",
    href: "/marketplace",
    colorVar: "hsl(var(--accent-skill))",
  },
  {
    title: "RAG Ops MCP",
    type: "MCP Server",
    description: "Unified retrieval, chunk scoring, and eval traces for production QA pipelines.",
    installs: "1.7k installs",
    rating: "4.8",
    href: "/marketplace",
    colorVar: "hsl(var(--accent-mcp))",
  },
  {
    title: "Creator Revenue Pack",
    type: "Pack",
    description: "Listing templates, launch automations, and payout dashboards for new publishers.",
    installs: "980 installs",
    rating: "4.7",
    href: "/marketplace",
    colorVar: "hsl(var(--accent-pack))",
  },
];

const HOW_IT_WORKS = [
  {
    icon: ShieldCheck,
    title: "Verify",
    description: "Connect Phantom wallet and establish creator identity before publishing.",
  },
  {
    icon: Sparkles,
    title: "Publish",
    description: "Ship MCP servers, skills, agents, or packs with versioned metadata and pricing.",
  },
  {
    icon: Workflow,
    title: "Monetize",
    description: "Track installs, ratings, and payouts from a single creator dashboard.",
  },
];

export default function HomePage() {
  return (
    <div className="relative flex min-h-screen flex-col overflow-x-hidden tech-grid scanlines grain">
      <div
        className="pointer-events-none fixed inset-0 z-0"
        aria-hidden="true"
        style={{
          background:
            "radial-gradient(ellipse 80% 45% at 50% -5%, hsl(183 100% 50% / 0.12) 0%, transparent 70%)",
        }}
      />
      <div
        className="pointer-events-none fixed inset-0 z-0"
        aria-hidden="true"
        style={{
          background:
            "radial-gradient(circle at 85% 22%, hsl(270 85% 65% / 0.11) 0%, transparent 32%), radial-gradient(circle at 12% 70%, hsl(38 95% 55% / 0.09) 0%, transparent 30%)",
        }}
      />

      <Navbar />

      <main className="relative z-10 flex-1">
        <section className="mx-auto max-w-6xl px-4 pt-32 pb-20 sm:px-6">
          <div className="grid items-start gap-10 lg:grid-cols-[1.1fr_0.9fr] lg:gap-14">
            <div>
              <div
                className="mb-7 inline-flex animate-fade-in items-center gap-2 rounded-full border px-4 py-1.5 text-xs font-mono font-medium"
                style={{
                  borderColor: "hsl(var(--primary) / 0.3)",
                  background: "hsl(var(--primary) / 0.08)",
                  color: "hsl(var(--primary))",
                }}
              >
                <span
                  className="h-1.5 w-1.5 rounded-full animate-pulse-glow"
                  style={{ background: "hsl(var(--primary))" }}
                />
                Solana-powered | Community-driven | Open marketplace
              </div>

              <h1 className="stagger mb-6 max-w-3xl text-5xl font-bold leading-[1.03] tracking-tight sm:text-6xl lg:text-7xl">
                <span className="block text-foreground">Ship, discover, and scale</span>
                <span className="block neon-text" style={{ color: "hsl(var(--primary))" }}>
                  AI agents and tools
                </span>
              </h1>

              <p className="animate-fade-in mb-10 max-w-2xl text-lg text-muted-foreground [animation-delay:0.25s] opacity-0">
                Discover, share, and monetize MCP servers, agent skills, custom agents, and packs.
                Connect your wallet, publish with confidence, and grow in a high-signal builder ecosystem.
              </p>

              <div className="animate-fade-in mb-10 flex flex-wrap items-center gap-4 [animation-delay:0.4s] opacity-0">
                <Link
                  href="/marketplace"
                  className="group flex items-center gap-2 rounded-xl px-6 py-3 text-sm font-semibold transition-all duration-300"
                  style={{
                    background: "hsl(var(--primary))",
                    color: "hsl(var(--primary-foreground))",
                    boxShadow: "0 0 24px hsl(var(--primary) / 0.4), 0 0 60px hsl(var(--primary) / 0.12)",
                  }}
                >
                  Browse Marketplace
                  <ArrowRight className="h-4 w-4 transition-transform duration-200 group-hover:translate-x-1" />
                </Link>
                <Link
                  href="/publish"
                  className="group flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-6 py-3 text-sm font-semibold text-foreground/80 transition-all duration-200 hover:border-white/20 hover:bg-white/10 hover:text-foreground"
                >
                  Publish a Listing
                  <ArrowUpRight className="h-4 w-4 transition-transform duration-200 group-hover:-translate-y-0.5 group-hover:translate-x-0.5" />
                </Link>
              </div>

              <div className="animate-fade-in grid grid-cols-2 gap-4 [animation-delay:0.55s] opacity-0 sm:grid-cols-4">
                {STATS.map(({ label, value }) => (
                  <div
                    key={label}
                    className="rounded-xl border border-white/8 bg-card/55 px-4 py-3 backdrop-blur-sm"
                  >
                    <div className="font-mono text-xl font-bold" style={{ color: "hsl(var(--primary))" }}>
                      {value}
                    </div>
                    <div className="mt-1 text-[11px] uppercase tracking-[0.18em] text-muted-foreground">
                      {label}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <aside className="animate-fade-in relative overflow-hidden rounded-2xl border border-white/10 bg-card/75 p-6 backdrop-blur-lg [animation-delay:0.3s] opacity-0">
              <div
                className="pointer-events-none absolute inset-0"
                aria-hidden="true"
                style={{
                  background:
                    "radial-gradient(circle at 8% 18%, hsl(var(--primary) / 0.2), transparent 38%), radial-gradient(circle at 90% 80%, hsl(270 85% 65% / 0.16), transparent 32%)",
                }}
              />
              <div className="relative">
                <div className="mb-6 flex items-center justify-between">
                  <div>
                    <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-muted-foreground">
                      Live Marketplace Pulse
                    </p>
                    <h2 className="mt-1 text-xl font-semibold">Realtime ecosystem signal</h2>
                  </div>
                  <div className="flex items-center gap-1.5 rounded-full border border-primary/35 bg-primary/10 px-2.5 py-1 text-[10px] font-mono uppercase tracking-[0.16em] text-primary">
                    <Activity className="h-3 w-3" />
                    Live
                  </div>
                </div>

                <div className="space-y-2.5">
                  {LIVE_FEED.map(({ label, value, detail }) => (
                    <div
                      key={label}
                      className="flex items-center justify-between rounded-xl border border-white/10 bg-background/55 px-4 py-3"
                    >
                      <div>
                        <p className="text-sm font-medium text-foreground">{label}</p>
                        <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-muted-foreground">
                          {detail}
                        </p>
                      </div>
                      <span className="font-mono text-lg font-semibold text-primary">{value}</span>
                    </div>
                  ))}
                </div>
              </div>
            </aside>
          </div>

          <div className="mt-10 overflow-hidden rounded-xl border border-white/10 bg-background/70 backdrop-blur-sm">
            <div className="signal-track">
              {[...Array(2)].map((_, idx) => (
                <div key={idx} className="flex shrink-0 items-center gap-3 px-2 py-2.5">
                  <span className="signal-pill">New skill drops daily</span>
                  <span className="signal-pill">SOL-native creator payouts</span>
                  <span className="signal-pill">One-click installs</span>
                  <span className="signal-pill">Wallet-verified publishers</span>
                  <span className="signal-pill">Marketplace reputation layer</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-4 pb-24 sm:px-6">
          <div className="mb-10 flex items-end justify-between">
            <div>
              <p className="mb-1 font-mono text-xs uppercase tracking-widest text-muted-foreground">Explore</p>
              <h2 className="text-3xl font-bold">Browse by type</h2>
            </div>
            <Link
              href="/marketplace"
              className="hidden items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground sm:flex"
            >
              View all <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>

          <div className="stagger grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {CATEGORIES.map(({ icon: Icon, label, description, href, glowClass, colorVar, bg, border, count }) => (
              <Link
                key={href}
                href={href}
                className={`group relative flex flex-col gap-4 rounded-2xl border p-6 transition-all duration-300 hover:-translate-y-1 hover:${glowClass}`}
                style={{ background: bg, borderColor: border }}
              >
                <div
                  className="flex h-10 w-10 items-center justify-center rounded-xl"
                  style={{ background: `color-mix(in srgb, ${colorVar} 15%, transparent)` }}
                >
                  <Icon className="h-5 w-5" style={{ color: colorVar }} />
                </div>

                <div className="flex-1">
                  <h3 className="font-semibold text-foreground">{label}</h3>
                  <p className="mt-1 text-sm text-muted-foreground">{description}</p>
                </div>

                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs" style={{ color: colorVar }}>
                    {count} listings
                  </span>
                  <ArrowRight
                    className="h-4 w-4 text-muted-foreground transition-all duration-200 group-hover:translate-x-1"
                    style={{ color: colorVar }}
                  />
                </div>

                <div
                  className="absolute right-4 top-4 h-2 w-2 rounded-full animate-pulse-glow"
                  style={{ background: colorVar }}
                />
              </Link>
            ))}
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-4 pb-24 sm:px-6">
          <div className="mb-9 flex items-end justify-between">
            <div>
              <p className="mb-1 font-mono text-xs uppercase tracking-widest text-muted-foreground">Featured</p>
              <h2 className="text-3xl font-bold">High-signal builds this week</h2>
            </div>
            <Link
              href="/marketplace"
              className="hidden items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground sm:flex"
            >
              Open marketplace <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>

          <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
            {FEATURED_BUILDS.map(({ title, type, description, installs, rating, href, colorVar }) => (
              <Link
                key={title}
                href={href}
                className="group relative overflow-hidden rounded-2xl border border-white/10 bg-card/70 p-6 transition-all duration-300 hover:-translate-y-1 hover:border-white/20"
              >
                <div
                  className="pointer-events-none absolute -right-12 -top-12 h-32 w-32 rounded-full blur-2xl"
                  style={{ background: `${colorVar}33` }}
                  aria-hidden="true"
                />
                <p className="font-mono text-[11px] uppercase tracking-[0.18em]" style={{ color: colorVar }}>
                  {type}
                </p>
                <h3 className="mt-2 text-xl font-semibold">{title}</h3>
                <p className="mt-3 text-sm leading-relaxed text-muted-foreground">{description}</p>
                <div className="mt-6 flex items-center justify-between text-xs">
                  <span className="font-mono uppercase tracking-[0.16em] text-muted-foreground">{installs}</span>
                  <span className="flex items-center gap-1.5 font-mono text-foreground">
                    <Star className="h-3.5 w-3.5 fill-current text-amber-400" />
                    {rating}
                  </span>
                </div>
                <div className="mt-5 flex items-center gap-1.5 text-sm font-medium text-primary">
                  View listing
                  <ArrowRight className="h-4 w-4 transition-transform duration-200 group-hover:translate-x-1" />
                </div>
              </Link>
            ))}
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-4 pb-24 sm:px-6">
          <div className="rounded-2xl border border-white/10 bg-card/60 p-6 sm:p-8">
            <div className="mb-8">
              <p className="mb-1 font-mono text-xs uppercase tracking-widest text-muted-foreground">Workflow</p>
              <h2 className="text-3xl font-bold">From creator idea to monetized install</h2>
            </div>

            <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
              {HOW_IT_WORKS.map(({ icon: Icon, title, description }, index) => (
                <div key={title} className="rounded-xl border border-white/10 bg-background/50 p-5">
                  <div className="mb-4 flex items-center justify-between">
                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/12 text-primary">
                      <Icon className="h-4.5 w-4.5" />
                    </div>
                    <span className="font-mono text-xs text-muted-foreground">0{index + 1}</span>
                  </div>
                  <h3 className="text-lg font-semibold">{title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{description}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="border-t border-white/5 py-20" style={{ background: "hsl(240 20% 4% / 0.8)" }}>
          <div className="mx-auto grid max-w-6xl gap-10 px-4 sm:px-6 lg:grid-cols-[1.08fr_0.92fr] lg:items-center">
            <div>
              <p className="mb-3 font-mono text-xs uppercase tracking-widest text-muted-foreground">Community</p>
              <h2 className="mb-4 max-w-xl text-3xl font-bold">Built for builders, by builders</h2>
              <p className="max-w-xl text-muted-foreground">
                Publish MCP servers, skills, and agents. Earn SOL when others use your work.
                Keep ownership, build reputation, and grow with a focused technical community.
              </p>

              <div className="mt-8 flex flex-wrap items-center gap-6">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Star className="h-4 w-4 fill-amber-400 text-amber-400" />
                  Peer-reviewed ratings
                </div>
                <div className="h-4 w-px bg-border" />
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Download className="h-4 w-4" />
                  One-click installs
                </div>
                <div className="h-4 w-px bg-border" />
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <span className="font-mono text-xs" style={{ color: "hsl(var(--primary))" }}>
                    O
                  </span>
                  SOL-native payments
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <div className="rounded-xl border border-white/10 bg-card/65 p-4">
                <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-muted-foreground">
                  Creator retention
                </p>
                <p className="mt-1 text-2xl font-semibold text-primary">87%</p>
              </div>
              <div className="rounded-xl border border-white/10 bg-card/65 p-4">
                <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-muted-foreground">
                  Average payout cycle
                </p>
                <p className="mt-1 text-2xl font-semibold text-foreground">24h settlement</p>
              </div>
              <div className="rounded-xl border border-white/10 bg-card/65 p-4">
                <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-muted-foreground">
                  Trust surface
                </p>
                <p className="mt-1 flex items-center gap-2 text-sm text-foreground">
                  <ShieldCheck className="h-4 w-4 text-primary" />
                  Wallet verification + signed provenance + version history
                </p>
              </div>
            </div>
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-4 py-14 sm:px-6">
          <div className="rounded-2xl border border-primary/25 bg-primary/7 px-6 py-7 sm:flex sm:items-center sm:justify-between">
            <div>
              <p className="font-mono text-xs uppercase tracking-[0.2em] text-primary">Launch your first listing</p>
              <h2 className="mt-2 text-2xl font-bold sm:text-3xl">Start publishing in under five minutes</h2>
            </div>
            <Link
              href="/publish"
              className="mt-5 inline-flex items-center gap-2 rounded-xl bg-primary px-5 py-3 text-sm font-semibold text-primary-foreground transition-all duration-300 hover:shadow-[0_0_24px_hsl(var(--primary)_/_0.4)] sm:mt-0"
            >
              Open Publish Flow
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </section>
      </main>
    </div>
  );
}
