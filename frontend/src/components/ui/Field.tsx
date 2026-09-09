import * as React from "react";
import { cn } from "@/lib/cn";

// ── Field ────────────────────────────────────────────────────────────────

export interface FieldProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Unique field id — links label, input, and error via aria attributes. */
  id: string;
  /** Visible label text. */
  label: string;
  /** Error message shown below the input. Sets aria-invalid. */
  error?: string;
  /** Help text shown below the input when there is no error. */
  hint?: string;
  /** Marks the field as required. */
  required?: boolean;
  /** Disables the field. */
  disabled?: boolean;
}

export function Field({
  id,
  label,
  error,
  hint,
  required = false,
  disabled = false,
  className,
  children,
  ...props
}: FieldProps) {
  const errorId = `${id}-error`;
  const hintId = `${id}-hint`;
  const describedBy = [
    error ? errorId : undefined,
    hint && !error ? hintId : undefined,
  ]
    .filter(Boolean)
    .join(" ") || undefined;

  return (
    <div
      className={cn(
        "flex flex-col gap-1.5",
        disabled && "opacity-50 pointer-events-none",
        className
      )}
      {...props}
    >
      <label
        htmlFor={id}
        className="text-sm font-medium text-text-primary"
      >
        {label}
        {required && (
          <span className="text-feedback-danger ml-0.5" aria-hidden="true">
            *
          </span>
        )}
      </label>

      {/* Slot for the actual input element — consumer must pass id={id} */}
      {React.isValidElement(children)
        ? React.cloneElement(children as React.ReactElement<Record<string, unknown>>, {
            id,
            "aria-describedby": describedBy,
            "aria-invalid": error ? true : undefined,
            "aria-required": required || undefined,
            disabled,
          })
        : children}

      {error && (
        <p id={errorId} role="alert" className="text-xs text-feedback-danger">
          {error}
        </p>
      )}
      {hint && !error && (
        <p id={hintId} className="text-xs text-text-muted">
          {hint}
        </p>
      )}
    </div>
  );
}

// ── Input (styled) ───────────────────────────────────────────────────────

type InputProps = React.InputHTMLAttributes<HTMLInputElement>;

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, ...props }, ref) => {
    return (
      <input
        ref={ref}
        className={cn(
          "h-11 w-full rounded-lg border border-border-subtle bg-surface-muted px-3.5 text-sm text-text-primary",
          "placeholder:text-text-muted",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:border-border-focus",
          "disabled:cursor-not-allowed disabled:opacity-50",
          "aria-invalid:border-border-error aria-invalid:ring-feedback-danger/30",
          "transition-colors duration-fast",
          className
        )}
        {...props}
      />
    );
  }
);
Input.displayName = "Input";

// ── Textarea (styled) ────────────────────────────────────────────────────

type TextareaProps = React.TextareaHTMLAttributes<HTMLTextAreaElement>;

export const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, ...props }, ref) => {
    return (
      <textarea
        ref={ref}
        className={cn(
          "min-h-[5rem] w-full rounded-lg border border-border-subtle bg-surface-muted px-3.5 py-2.5 text-sm text-text-primary",
          "placeholder:text-text-muted",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:border-border-focus",
          "disabled:cursor-not-allowed disabled:opacity-50",
          "aria-invalid:border-border-error aria-invalid:ring-feedback-danger/30",
          "transition-colors duration-fast resize-y",
          className
        )}
        {...props}
      />
    );
  }
);
Textarea.displayName = "Textarea";
