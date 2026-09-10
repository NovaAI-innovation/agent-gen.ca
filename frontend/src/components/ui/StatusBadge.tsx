import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/cn";

const statusBadgeVariants = cva(
  "inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium whitespace-nowrap",
  {
    variants: {
      status: {
        draft: "bg-surface-muted text-text-secondary border border-border-subtle",
        pending: "bg-feedback-warning-muted text-feedback-warning border border-feedback-warning/20",
        approved: "bg-feedback-success-muted text-feedback-success border border-feedback-success/20",
        published: "bg-feedback-success-muted text-feedback-success border border-feedback-success/20",
        rejected: "bg-feedback-danger-muted text-feedback-danger border border-feedback-danger/20",
        suspended: "bg-feedback-danger-muted text-feedback-danger border border-feedback-danger/20",
        active: "bg-feedback-success-muted text-feedback-success border border-feedback-success/20",
        expired: "bg-surface-muted text-text-muted border border-border-subtle",
        error: "bg-feedback-danger-muted text-feedback-danger border border-feedback-danger/20",
        scanning: "bg-feedback-info-muted text-feedback-info border border-feedback-info/20",
        success: "bg-feedback-success-muted text-feedback-success border border-feedback-success/20",
        info: "bg-feedback-info-muted text-feedback-info border border-feedback-info/20",
      },
    },
    defaultVariants: {
      status: "draft",
    },
  }
);

const dotColors: Record<string, string> = {
  draft: "bg-text-muted",
  pending: "bg-feedback-warning animate-pulse",
  approved: "bg-feedback-success",
  published: "bg-feedback-success",
  rejected: "bg-feedback-danger",
  suspended: "bg-feedback-danger",
  active: "bg-feedback-success",
  expired: "bg-text-muted",
  error: "bg-feedback-danger",
  scanning: "bg-feedback-info animate-pulse",
  success: "bg-feedback-success",
  info: "bg-feedback-info",
};

export interface StatusBadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof statusBadgeVariants> {
  /** Override the label text. Defaults to the capitalized status value. */
  label?: string;
}

export function StatusBadge({
  status = "draft",
  label,
  className,
  ...props
}: StatusBadgeProps) {
  const displayLabel = label ?? status ?? "draft";
  const dotColor = dotColors[status ?? "draft"] ?? "bg-text-muted";

  return (
    <span
      className={cn(statusBadgeVariants({ status }), className)}
      role="status"
      aria-label={displayLabel}
      {...props}
    >
      <span className={cn("inline-block h-1.5 w-1.5 rounded-full", dotColor)} aria-hidden="true" />
      {displayLabel}
    </span>
  );
}
