import type { ReactNode } from "react";
import type { LucideIcon } from "lucide-react";
import { cn } from "@/lib/cn";
import { Panel } from "@/components/ui/Panel";

export interface SignalStat {
  label: string;
  value: string;
}

export interface PageHeaderConfig {
  icon: LucideIcon;
  eyebrow?: string;
  title: string;
  subtitle: string;
  accentClassName?: string;
  stats?: SignalStat[];
  actions?: ReactNode;
}

interface PageHeaderProps extends PageHeaderConfig {
  className?: string;
}

export function PageHeader({
  icon: Icon,
  eyebrow = "Mission Control",
  title,
  subtitle,
  accentClassName,
  stats,
  actions,
  className,
}: PageHeaderProps) {
  return (
    <Panel className={cn("relative overflow-hidden", className)} padding="lg">
      <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-[linear-gradient(90deg,transparent,hsl(var(--border-focus)),transparent)]" aria-hidden="true" />
      <div className="relative flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <div className="mb-3 inline-flex items-center gap-2">
            <span className="rounded-full border border-border-subtle bg-surface-muted px-2.5 py-1 font-mono text-[10px] uppercase tracking-[0.18em] text-text-muted">
              {eyebrow}
            </span>
          </div>

          <div className="flex items-start gap-3">
            <div className={cn("flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-border-subtle bg-surface-muted", accentClassName)}>
              <Icon className="h-5 w-5" />
            </div>
            <div className="min-w-0">
              <h1 className="font-display text-3xl font-bold tracking-tight text-text-primary sm:text-4xl">{title}</h1>
              <p className="mt-2 max-w-2xl text-sm text-text-secondary sm:text-base">{subtitle}</p>
            </div>
          </div>

          {stats && stats.length > 0 ? (
            <div className="mt-5 flex flex-wrap gap-2.5">
              {stats.map((stat) => (
                <div key={stat.label} className="rounded-lg border border-border-subtle bg-surface-muted px-3 py-2">
                  <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-text-muted">{stat.label}</p>
                  <p className="mt-1 font-mono text-sm font-semibold text-text-primary">{stat.value}</p>
                </div>
              ))}
            </div>
          ) : null}
        </div>

        {actions ? <div className="shrink-0">{actions}</div> : null}
      </div>
    </Panel>
  );
}
