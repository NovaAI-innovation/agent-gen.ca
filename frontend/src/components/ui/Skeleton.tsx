import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/cn";

const skeletonVariants = cva(
  "relative overflow-hidden bg-surface-muted rounded-[var(--radius)]",
  {
    variants: {
      animate: {
        pulse: "animate-pulse",
        shimmer: "skeleton",
        none: "",
      },
    },
    defaultVariants: {
      animate: "shimmer",
    },
  }
);

export interface SkeletonProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof skeletonVariants> {
  /** Width — any CSS value. Defaults to 100%. */
  width?: string | number;
  /** Height — any CSS value. Defaults to 1rem. */
  height?: string | number;
  /** Render as a circle (e.g. avatar placeholder). */
  circle?: boolean;
}

export function Skeleton({
  animate,
  width,
  height,
  circle = false,
  className,
  style,
  ...props
}: SkeletonProps) {
  return (
    <div
      aria-hidden="true"
      className={cn(
        skeletonVariants({ animate }),
        circle && "rounded-full",
        className
      )}
      style={{
        width: width ?? "100%",
        height: height ?? "1rem",
        ...style,
      }}
      {...props}
    />
  );
}

// ── Composite skeleton layouts ───────────────────────────────────────────

/** Card-shaped skeleton for marketplace listing placeholders. */
export function CardSkeleton({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("flex flex-col gap-3 p-4 rounded-xl border border-border-subtle bg-surface-elevated", className)}
      aria-hidden="true"
      {...props}
    >
      <Skeleton height="10rem" />
      <Skeleton width="70%" height="1rem" />
      <Skeleton width="50%" height="0.75rem" />
      <div className="flex gap-2 mt-1">
        <Skeleton width="3.5rem" height="1.5rem" />
        <Skeleton width="3.5rem" height="1.5rem" />
      </div>
    </div>
  );
}

/** Row-shaped skeleton for table/list placeholders. */
export function RowSkeleton({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("flex items-center gap-3 p-3", className)}
      aria-hidden="true"
      {...props}
    >
      <Skeleton circle width="2rem" height="2rem" />
      <div className="flex-1 flex flex-col gap-1.5">
        <Skeleton width="60%" height="0.75rem" />
        <Skeleton width="40%" height="0.625rem" />
      </div>
      <Skeleton width="4rem" height="1.5rem" />
    </div>
  );
}
