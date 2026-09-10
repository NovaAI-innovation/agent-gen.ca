"use client";

import { useState } from "react";
import {
  CheckCircle2,
  Cpu,
  ExternalLink,
  Server,
  Shield,
  Zap,
  GitBranch,
  Database,
  Cloud,
  Layers,
  BarChart3,
  Box,
  Globe,
  Lock,
  RefreshCw,
  Terminal,
  Workflow,
} from "lucide-react";
import { AppShell } from "@/components/templates/AppShell";
import { Panel } from "@/components/ui/Panel";
import { cn } from "@/lib/cn";

/* ─── Service data ─────────────────────────────────────── */

interface Benefit {
  icon: typeof Box;
  title: string;
  description: string;
}

interface Integration {
  icon: typeof Box;
  title: string;
  description: string;
}

interface ServiceResource {
  id: string;
  name: string;
  tagline: string;
  icon: typeof Box;
  accent: string; // Tailwind text colour class
  bgAccent: string; // Tailwind bg border colour class
  useCases: string[];
  benefits: Benefit[];
  integrations: Integration[];
  disclosure?: string;
  referralUrl?: string;
  referralLabel?: string;
}

const SERVICES: ServiceResource[] = [
  {
    id: "hostinger-vps",
    name: "Hostinger VPS",
    tagline: "KVM-based virtual private servers with enterprise-grade hardware at budget-friendly prices",
    icon: Server,
    accent: "text-cyan-300",
    bgAccent: "border-cyan-500/30 bg-cyan-500/10",
    useCases: [
      "Self-hosting AI agents like Hermes Agent, OpenClaw, or n8n with persistent memory and workflow automation",
      "Running production web applications, APIs, and databases with dedicated resources and full root access",
      "Deploying open-source tools — Nextcloud, GitLab, WordPress, Docker-based stacks — via one-click application catalog",
      "Building and testing CI/CD pipelines, staging environments, or container orchestration experiments",
      "Hosting high-traffic ecommerce or media sites where shared hosting no longer cuts it",
    ],
    benefits: [
      {
        icon: Cpu,
        title: "AMD EPYC Processors",
        description: "Enterprise-grade CPUs across all tiers deliver strong single-threaded and multi-core performance unusual at this price point.",
      },
      {
        icon: Database,
        title: "NVMe SSD Storage",
        description: "Even the entry-level KVM 1 plan ships NVMe storage, translating to faster package installs, quicker DB queries, and snappier ops vs SATA SSD hosts.",
      },
      {
        icon: Shield,
        title: "Free Weekly Backups",
        description: "Automated weekly backups plus manual snapshot support included at no extra cost — a common premium add-on elsewhere.",
      },
      {
        icon: Globe,
        title: "Global Data Centers",
        description: "Points of presence across North America, Europe, Asia, and South America with 1 Gbps network ports on all plans.",
      },
      {
        icon: Zap,
        title: "AI-Managed Control Panel",
        description: "Kodee AI assistant for server monitoring and common tasks. AI web terminal for quick SSH access from any browser.",
      },
      {
        icon: Layers,
        title: "One-Click App Catalog",
        description: "Deploy Docker, n8n, WordPress, GitLab, Hermes Agent, OpenClaw, and 80+ other applications without manual setup.",
      },
    ],
    integrations: [
      {
        icon: Terminal,
        title: "Direct SSH + Root Access",
        description: "Full root access means you control the entire stack — install any package, tune any kernel parameter, run any service without restrictions.",
      },
      {
        icon: GitBranch,
        title: "Docker & Docker Compose",
        description: "Pre-installed Docker support via the app catalog or manual setup. Deploy multi-container stacks with Compose for reproducible environments.",
      },
      {
        icon: Cloud,
        title: "Hostinger VPS API",
        description: "Programmatic infrastructure management — automate deployments, scale resources, and integrate provisioning into your existing toolchain.",
      },
      {
        icon: Workflow,
        title: "n8n & AI Workflow Automation",
        description: "One-click n8n deployment turns your VPS into an automation hub. Connect APIs, databases, and AI models into production pipelines.",
      },
      {
        icon: Lock,
        title: "Firewall Management + Fail2ban",
        description: "Built-in firewall management via the control panel plus easy fail2ban setup for SSH brute-force protection out of the box.",
      },
      {
        icon: RefreshCw,
        title: "Snapshot-Driven Recovery",
        description: "Manual snapshots before major changes + weekly automated backups create a safety net. Restore from any point in minutes.",
      },
    ],
    disclosure:
      "I participate in Hostinger's affiliate program. If you sign up through the link below, I may earn a commission at no extra cost to you. I've been a paying customer since before joining the program.",
    referralUrl: "https://www.hostinger.com/vps-hosting",
    referralLabel: "Explore Hostinger VPS Plans",
  },
];

/* ─── Tab Button ────────────────────────────────────────── */

function TabButton({
  active,
  icon: Icon,
  label,
  onClick,
}: {
  active: boolean;
  icon: typeof Box;
  label: string;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "flex items-center gap-2.5 rounded-xl border px-4 py-3 text-left text-sm font-semibold transition-all duration-200",
        active
          ? "border-border-focus bg-action-primary/12 text-action-primary shadow-[0_0_16px_hsl(var(--action-primary)/0.12)]"
          : "border-border-subtle bg-surface-elevated text-text-secondary hover:border-border-strong hover:bg-surface-hover hover:text-text-primary"
      )}
    >
      <div
        className={cn(
          "flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border",
          active ? "border-border-focus bg-action-primary/15" : "border-border-subtle bg-surface-muted"
        )}
      >
        <Icon className={cn("h-4 w-4", active ? "text-action-primary" : "text-text-muted")} />
      </div>
      <span className="truncate">{label}</span>
    </button>
  );
}

/* ─── Section sub-components ───────────────────────────── */

function SectionHeading({ icon: Icon, label }: { icon: typeof Box; label: string }) {
  return (
    <div className="mb-5 flex items-center gap-2.5">
      <div className="flex h-7 w-7 items-center justify-center rounded-lg border border-border-subtle bg-surface-muted">
        <Icon className="h-3.5 w-3.5 text-text-muted" />
      </div>
      <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-text-muted">{label}</span>
    </div>
  );
}

function UseCaseList({ items }: { items: string[] }) {
  return (
    <div className="grid gap-2.5 sm:grid-cols-2">
      {items.map((item) => (
        <div
          key={item}
          className="flex items-start gap-2.5 rounded-xl border border-border-subtle bg-surface-muted/60 px-4 py-3"
        >
          <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-action-primary" />
          <span className="text-sm text-text-secondary leading-snug">{item}</span>
        </div>
      ))}
    </div>
  );
}

function BenefitCard({ icon: Icon, title, description }: Benefit) {
  return (
    <Panel className="h-full transition-transform duration-200 hover:-translate-y-0.5" padding="md">
      <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-lg border border-border-subtle bg-surface-muted">
        <Icon className="h-4 w-4 text-action-primary" />
      </div>
      <h3 className="text-sm font-semibold text-text-primary">{title}</h3>
      <p className="mt-1.5 text-sm leading-relaxed text-text-secondary">{description}</p>
    </Panel>
  );
}

function IntegrationCard({ icon: Icon, title, description }: Integration) {
  return (
    <div className="rounded-xl border border-border-subtle bg-surface-muted/50 p-4 transition-colors duration-200 hover:border-border-strong">
      <div className="flex items-start gap-3">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-border-subtle bg-surface-muted">
          <Icon className="h-3.5 w-3.5 text-text-muted" />
        </div>
        <div className="min-w-0">
          <h3 className="text-sm font-semibold text-text-primary">{title}</h3>
          <p className="mt-1 text-sm leading-relaxed text-text-secondary">{description}</p>
        </div>
      </div>
    </div>
  );
}

/* ─── Tab Content Panels ────────────────────────────────── */

function ServiceTab({ service }: { service: ServiceResource }) {
  return (
    <div className="space-y-10 animate-[fade-up_0.35s_ease-out]">
      {/* Hero */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <div className="mb-2 flex items-center gap-2">
            <div
              className={cn(
                "flex h-10 w-10 items-center justify-center rounded-xl border",
                service.bgAccent
              )}
            >
              <service.icon className={cn("h-5 w-5", service.accent)} />
            </div>
            <span className="rounded-full border border-border-subtle bg-surface-muted px-2.5 py-1 font-mono text-[10px] uppercase tracking-[0.18em] text-text-muted">
              Curated Service
            </span>
          </div>
          <h2 className="font-display text-2xl font-bold tracking-tight text-text-primary sm:text-3xl">
            {service.name}
          </h2>
          <p className="mt-1.5 max-w-2xl text-sm text-text-secondary sm:text-base">{service.tagline}</p>
        </div>

        {service.referralUrl ? (
          <a
            href={service.referralUrl}
            target="_blank"
            rel="noopener noreferrer"
            className={cn(
              "inline-flex shrink-0 items-center gap-2 rounded-xl border px-5 py-2.5 text-sm font-semibold transition-all duration-200",
              "border-border-focus bg-action-primary/12 text-action-primary hover:bg-action-primary/20 hover:shadow-[0_0_20px_hsl(var(--action-primary)/0.18)]"
            )}
          >
            {service.referralLabel ?? "Learn More"}
            <ExternalLink className="h-3.5 w-3.5" />
          </a>
        ) : null}
      </div>

      {/* Use Cases */}
      <div>
        <SectionHeading icon={BarChart3} label="Use Cases" />
        <UseCaseList items={service.useCases} />
      </div>

      {/* Benefits */}
      <div>
        <SectionHeading icon={Zap} label="Key Benefits" />
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {service.benefits.map((benefit) => (
            <BenefitCard key={benefit.title} {...benefit} />
          ))}
        </div>
      </div>

      {/* Proposed Integrations / Improvements */}
      <div>
        <SectionHeading icon={GitBranch} label="Integration & Improvement Opportunities" />
        <div className="grid gap-2.5 sm:grid-cols-2">
          {service.integrations.map((int) => (
            <IntegrationCard key={int.title} {...int} />
          ))}
        </div>
      </div>

      {/* Disclosure */}
      {service.disclosure ? (
        <Panel tone="muted" padding="sm" className="text-center">
          <p className="text-xs leading-relaxed text-text-muted">{service.disclosure}</p>
        </Panel>
      ) : null}
    </div>
  );
}

/* ─── Main Page Component ───────────────────────────────── */

export default function ResourcesPage() {
  const [activeTab, setActiveTab] = useState(SERVICES.length > 0 ? SERVICES[0].id : null);
  const activeService = SERVICES.find((s) => s.id === activeTab);
  // Track how many empty placeholder slots to show (growing library)
  const PLACEHOLDER_SLOTS = 3;

  return (
    <AppShell>
      {/* Page Header */}
      <div className="mb-2">
        <div className="mb-3 inline-flex items-center gap-2">
          <span className="rounded-full border border-border-subtle bg-surface-muted px-2.5 py-1 font-mono text-[10px] uppercase tracking-[0.18em] text-text-muted">
            Knowledge Base
          </span>
        </div>
        <h1 className="font-display text-3xl font-bold tracking-tight text-text-primary sm:text-4xl">
          Curated <span className="neon-text text-action-primary">Infrastructure Resources</span>
        </h1>
        <p className="mt-2 max-w-2xl text-sm text-text-secondary sm:text-base">
          A growing library of hands-on guides covering VPS management, hosting infrastructure, and
          tool integrations. Each resource includes use cases, benefits, and actionable improvement
          opportunities — built from real deployment experience.
        </p>
      </div>

      <div className="mt-6 flex flex-col gap-6 lg:flex-row">
        {/* Tab Navigation — sidebar on desktop, horizontal scroll on mobile */}
        <aside className="shrink-0 lg:w-64">
          <nav className="flex gap-2 overflow-x-auto pb-2 lg:flex-col lg:pb-0">
            {SERVICES.map((svc, i) => (
              <TabButton
                key={svc.id}
                active={activeTab === svc.id}
                icon={svc.icon}
                label={svc.name}
                onClick={() => setActiveTab(svc.id)}
              />
            ))}
            {/* Placeholder tabs for future services */}
            {Array.from({ length: PLACEHOLDER_SLOTS }, (_a, idx) => (
              <button
                key={`placeholder-${idx}`}
                type="button"
                disabled
                className={cn(
                  "flex items-center gap-2.5 rounded-xl border border-dashed px-4 py-3 text-left text-sm font-semibold",
                  "border-border-subtle text-text-muted/50 cursor-not-allowed"
                )}
              >
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-dashed border-border-subtle bg-surface-muted/50">
                  <Box className="h-4 w-4 text-text-muted/40" />
                </div>
                <span className="truncate">Coming Soon</span>
              </button>
            ))}
          </nav>

          {/* Library stats */}
          <div className="mt-4 hidden rounded-xl border border-border-subtle bg-surface-muted/60 px-4 py-3 lg:block">
            <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-text-muted">Service Library</p>
            <div className="mt-2 space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="text-xs text-text-secondary">Active guides</span>
                <span className="font-mono text-xs font-semibold text-action-primary">{SERVICES.length}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-text-secondary">Slots available</span>
                <span className="font-mono text-xs font-semibold text-text-muted">{PLACEHOLDER_SLOTS}</span>
              </div>
              <div className="mt-2 h-px bg-border-subtle" />
              <p className="pt-1 text-[10px] text-text-muted">New services added regularly</p>
            </div>
          </div>
        </aside>

        {/* Main Content Area */}
        <div className="min-w-0 flex-1">
          {activeService ? (
            <ServiceTab service={activeService} />
          ) : (
            <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-border-subtle bg-surface-muted/30 px-6 py-20 text-center">
              <Box className="mb-3 h-8 w-8 text-text-muted" />
              <p className="font-display text-lg font-semibold text-text-muted">Select a resource</p>
              <p className="mt-1 text-sm text-text-muted">
                Choose a service from the sidebar to view its guide.
              </p>
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}
