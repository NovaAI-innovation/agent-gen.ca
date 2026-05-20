import Link from "next/link";
import { Activity, ArrowRight, Bot, Download, Package, Server, ShieldCheck, Sparkles, Star, Workflow, Zap } from "lucide-react";
import { AppShell } from "@/components/templates/AppShell";
import { Button } from "@/components/ui/Button";
import { Panel } from "@/components/ui/Panel";

const CATEGORIES = [
  {
    icon: Server,
    label: "MCP Servers",
    description: "Model Context Protocol packages for production runtimes.",
    href: "/mcp-servers",
    accent: "text-cyan-300",
  },
  {
    icon: Zap,
    label: "Agent Skills",
    description: "Composable skills and reusable tools for agents.",
    href: "/agent-skills",
    accent: "text-amber-300",
  },
  {
    icon: Bot,
    label: "Custom Agents",
    description: "Full personalities and system bundles.",
    href: "/agents",
    accent: "text-lime-300",
  },
  {
    icon: Package,
    label: "Packs",
    description: "Curated bundles for fast deployment.",
    href: "/packs",
    accent: "text-violet-300",
  },
];

const SIGNALS = [
  { label: "Live listings", value: "500+" },
  { label: "Weekly installs", value: "8.1k" },
  { label: "Verified creators", value: "312" },
  { label: "Avg rating", value: "4.8/5" },
];

const FLOW = [
  {
    icon: ShieldCheck,
    title: "Verify",
    description: "Connect wallet and establish trusted creator identity.",
  },
  {
    icon: Sparkles,
    title: "Publish",
    description: "Ship listings with metadata, install docs, and pricing.",
  },
  {
    icon: Workflow,
    title: "Scale",
    description: "Track installs, retention, and payout performance.",
  },
];

export default function HomePage() {
  return (
    <AppShell>
      <section className="grid items-start gap-5 lg:grid-cols-[1.1fr_0.9fr]">
        <Panel className="relative overflow-hidden" padding="lg">
          <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-[linear-gradient(90deg,transparent,hsl(var(--primary)),transparent)]" />

          <span className="inline-flex items-center gap-2 rounded-full border border-action-primary/35 bg-action-primary/10 px-3 py-1 font-mono text-[10px] uppercase tracking-[0.18em] text-action-primary">
            <Activity className="h-3 w-3" />
            Mission control online
          </span>

          <h1 className="mt-6 max-w-3xl font-display text-5xl font-bold leading-[0.95] tracking-tight text-text-primary sm:text-6xl lg:text-7xl">
            Build, ship, and monetize <span className="neon-text text-action-primary">agent systems</span>
          </h1>

          <p className="mt-5 max-w-2xl text-base text-text-secondary sm:text-lg">
            agent-gen.ca is the marketplace for MCP servers, skills, custom agents, and packs. Designed for creator-grade publishing and buyer-grade discovery.
          </p>

          <div className="mt-7 flex flex-wrap gap-3">
            <Button asChild size="lg">
              <Link href="/marketplace">
                Explore marketplace
                <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
            <Button asChild size="lg" variant="secondary">
              <Link href="/publish">Start publishing</Link>
            </Button>
          </div>

          <div className="mt-8 grid grid-cols-2 gap-3 sm:grid-cols-4">
            {SIGNALS.map((signal) => (
              <div key={signal.label} className="rounded-xl border border-border-subtle bg-surface-muted/70 px-3 py-2.5">
                <p className="font-mono text-sm font-semibold text-text-primary">{signal.value}</p>
                <p className="mt-1 font-mono text-[10px] uppercase tracking-[0.18em] text-text-muted">{signal.label}</p>
              </div>
            ))}
          </div>
        </Panel>

        <Panel padding="lg" className="space-y-4">
          <div className="flex items-center justify-between">
            <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-text-muted">Live ecosystem pulse</p>
            <span className="rounded-full border border-action-primary/35 bg-action-primary/10 px-2.5 py-1 font-mono text-[10px] uppercase tracking-[0.18em] text-action-primary">
              LIVE
            </span>
          </div>

          {[
            ["New listings", "+24", "7 days"],
            ["Install success", "98.6%", "rolling 30d"],
            ["Avg setup", "48s", "one click"],
            ["Creator payout", "24h", "settlement"],
          ].map(([label, value, hint]) => (
            <div key={label} className="rounded-xl border border-border-subtle bg-surface-muted/70 px-4 py-3">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-sm text-text-primary">{label}</p>
                  <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-text-muted">{hint}</p>
                </div>
                <p className="font-mono text-lg font-semibold text-action-primary">{value}</p>
              </div>
            </div>
          ))}
        </Panel>
      </section>

      <section className="mt-8 overflow-hidden rounded-xl border border-border-subtle bg-surface-elevated/80">
        <div className="signal-track py-2">
          {[...Array(2)].map((_, idx) => (
            <div key={idx} className="flex shrink-0 items-center gap-3 px-2">
              <span className="signal-pill">Wallet-verified publishers</span>
              <span className="signal-pill">Signed provenance</span>
              <span className="signal-pill">SOL-native payouts</span>
              <span className="signal-pill">One-click installs</span>
              <span className="signal-pill">Creator reputation graph</span>
            </div>
          ))}
        </div>
      </section>

      <section className="mt-10 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {CATEGORIES.map(({ icon: Icon, label, description, href, accent }) => (
          <Link key={label} href={href}>
            <Panel className="h-full transition-transform duration-200 hover:-translate-y-1" padding="md">
              <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-xl border border-border-subtle bg-surface-muted">
                <Icon className={`h-5 w-5 ${accent}`} />
              </div>
              <h2 className="text-lg font-semibold text-text-primary">{label}</h2>
              <p className="mt-1 text-sm text-text-secondary">{description}</p>
              <div className={`mt-4 inline-flex items-center gap-1 text-sm ${accent}`}>
                View category <ArrowRight className="h-3.5 w-3.5" />
              </div>
            </Panel>
          </Link>
        ))}
      </section>

      <section className="mt-10 grid gap-5 lg:grid-cols-[1fr_0.95fr]">
        <Panel padding="lg">
          <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-text-muted">Creator workflow</p>
          <h2 className="mt-2 font-display text-3xl font-bold text-text-primary">From idea to monetized install</h2>
          <div className="mt-6 grid gap-3 md:grid-cols-3">
            {FLOW.map(({ icon: Icon, title, description }, index) => (
              <div key={title} className="rounded-xl border border-border-subtle bg-surface-muted/60 p-4">
                <div className="mb-3 flex items-center justify-between">
                  <Icon className="h-4 w-4 text-action-primary" />
                  <span className="font-mono text-[10px] text-text-muted">0{index + 1}</span>
                </div>
                <p className="font-semibold text-text-primary">{title}</p>
                <p className="mt-1 text-sm text-text-secondary">{description}</p>
              </div>
            ))}
          </div>
        </Panel>

        <Panel padding="lg" className="flex flex-col justify-between">
          <div>
            <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-text-muted">Trust layer</p>
            <h2 className="mt-2 font-display text-3xl font-bold text-text-primary">Built for credible builders</h2>
            <p className="mt-3 text-sm text-text-secondary">
              Provenance signatures, reputation scoring, and transparent version history establish confidence before every install.
            </p>
          </div>
          <div className="mt-6 space-y-2.5">
            <div className="flex items-center justify-between rounded-lg border border-border-subtle bg-surface-muted px-3 py-2">
              <span className="text-sm text-text-secondary">Average creator retention</span>
              <span className="font-mono text-sm text-text-primary">87%</span>
            </div>
            <div className="flex items-center justify-between rounded-lg border border-border-subtle bg-surface-muted px-3 py-2">
              <span className="text-sm text-text-secondary">Median install rating</span>
              <span className="flex items-center gap-1 font-mono text-sm text-text-primary">
                <Star className="h-3.5 w-3.5 fill-amber-400 text-amber-400" /> 4.8
              </span>
            </div>
            <div className="flex items-center justify-between rounded-lg border border-border-subtle bg-surface-muted px-3 py-2">
              <span className="text-sm text-text-secondary">Weekly downloads</span>
              <span className="flex items-center gap-1 font-mono text-sm text-text-primary">
                <Download className="h-3.5 w-3.5" /> 12.4k
              </span>
            </div>
          </div>
        </Panel>
      </section>
    </AppShell>
  );
}
