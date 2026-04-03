import type { LucideIcon } from "lucide-react";

interface MarketplaceHeaderProps {
  icon: LucideIcon;
  title: string;
  subtitle: string;
  accent: string;
  eyebrow?: string;
}

export function MarketplaceHeader({
  icon: Icon,
  title,
  subtitle,
  accent,
  eyebrow = "Marketplace",
}: MarketplaceHeaderProps) {
  return (
    <section className="relative mb-10 overflow-hidden rounded-2xl border border-white/10 bg-card/65 px-5 py-6 sm:px-7 sm:py-7">
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -right-16 -top-20 h-44 w-44 rounded-full blur-3xl"
        style={{ background: `${accent}30` }}
      />
      <div
        aria-hidden="true"
        className="pointer-events-none absolute left-0 top-0 h-px w-full"
        style={{ background: `linear-gradient(90deg, transparent, ${accent}, transparent)` }}
      />

      <div className="relative flex flex-col gap-4 sm:flex-row sm:items-center">
        <div
          className="flex h-12 w-12 items-center justify-center rounded-2xl border shrink-0"
          style={{ background: `${accent}1f`, borderColor: `${accent}50` }}
        >
          <Icon className="h-6 w-6" style={{ color: accent }} />
        </div>
        <div className="min-w-0">
          <p className="mb-1 font-mono text-[11px] uppercase tracking-[0.2em] text-muted-foreground">{eyebrow}</p>
          <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">{title}</h1>
          <p className="mt-1.5 max-w-2xl text-sm text-muted-foreground sm:text-base">{subtitle}</p>
        </div>
      </div>
    </section>
  );
}
