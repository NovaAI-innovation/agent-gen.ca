"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, AlertTriangle, CheckCircle, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { cn } from "@/lib/cn";

interface ReportDialogProps {
  open: boolean;
  onClose: () => void;
  entityType: "listing" | "release" | "user";
  entityId: string;
  entityTitle: string;
}

const REPORT_REASONS = [
  { code: "illegal_content", label: "Illegal content or activity" },
  { code: "malware", label: "Malware or security risk" },
  { code: "phishing", label: "Phishing or social engineering" },
  { code: "copyright", label: "Copyright or IP infringement" },
  { code: "misleading", label: "Misleading or deceptive listing" },
  { code: "harassment", label: "Harassment or discrimination" },
  { code: "spam", label: "Spam or manipulation" },
  { code: "other", label: "Other (specify below)" },
] as const;

type Stage = "form" | "success" | "error";

export function ReportDialog({ open, onClose, entityType, entityId, entityTitle }: ReportDialogProps) {
  const [reason, setReason] = useState<string>("");
  const [details, setDetails] = useState("");
  const [stage, setStage] = useState<Stage>("form");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  function reset() {
    setReason("");
    setDetails("");
    setStage("form");
    setIsSubmitting(false);
    setErrorMsg("");
  }

  function handleClose() {
    reset();
    onClose();
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!reason) return;

    setIsSubmitting(true);
    try {
      const res = await fetch("/api/reports", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          entity_type: entityType,
          entity_id: entityId,
          reason,
          details: details || null,
        }),
      });

      if (res.ok) {
        setStage("success");
      } else {
        const data = await res.json().catch(() => ({}));
        setErrorMsg(data.detail ?? "Something went wrong. Please try again.");
        setStage("error");
      }
    } catch {
      setErrorMsg("Network error. Please check your connection.");
      setStage("error");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <AnimatePresence>
      {open && (
        <>
          {/* Backdrop */}
          <motion.div
            className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={handleClose}
          />

          {/* Dialog */}
          <motion.div
            className="fixed left-1/2 top-1/2 z-50 w-full max-w-md -translate-x-1/2 -translate-y-1/2 px-4"
            initial={{ opacity: 0, scale: 0.95, y: "48%" }}
            animate={{ opacity: 1, scale: 1, y: "-50%" }}
            exit={{ opacity: 0, scale: 0.95, y: "48%" }}
            transition={{ duration: 0.2, ease: "easeOut" }}
          >
            <div className="rounded-2xl border border-border-subtle bg-surface-elevated p-6 shadow-2xl">
              {/* Header */}
              <div className="mb-5 flex items-start justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-9 w-9 items-center justify-center rounded-xl border border-amber-500/30 bg-amber-500/10">
                    <AlertTriangle className="h-4 w-4 text-amber-400" />
                  </div>
                  <div>
                    <h2 className="text-base font-semibold text-text-primary">Report {entityType}</h2>
                    <p className="mt-0.5 truncate text-sm text-text-muted" title={entityTitle}>
                      {entityTitle}
                    </p>
                  </div>
                </div>
                <button
                  onClick={handleClose}
                  className="rounded-lg p-1.5 text-text-muted transition-colors hover:bg-surface-hover hover:text-text-primary"
                  aria-label="Close"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>

              {/* Success state */}
              {stage === "success" && (
                <div className="flex flex-col items-center py-6 text-center">
                  <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full border border-emerald-500/30 bg-emerald-500/10">
                    <CheckCircle className="h-7 w-7 text-emerald-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-text-primary">Report submitted</h3>
                  <p className="mt-2 text-sm text-text-secondary">
                    Thank you. Our team will review the {entityType} and take appropriate action.
                  </p>
                  <Button className="mt-6" onClick={handleClose}>
                    Close
                  </Button>
                </div>
              )}

              {/* Error state */}
              {stage === "error" && (
                <div className="flex flex-col items-center py-6 text-center">
                  <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full border border-red-500/30 bg-red-500/10">
                    <X className="h-7 w-7 text-red-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-text-primary">Submission failed</h3>
                  <p className="mt-2 text-sm text-text-secondary">{errorMsg}</p>
                  <div className="mt-6 flex gap-3">
                    <Button variant="ghost" onClick={handleClose}>
                      Cancel
                    </Button>
                    <Button
                      onClick={() => {
                        setStage("form");
                        setErrorMsg("");
                      }}
                    >
                      Try again
                    </Button>
                  </div>
                </div>
              )}

              {/* Form */}
              {stage === "form" && (
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <label className="mb-2 block text-sm font-medium text-text-primary">
                      Reason for report <span className="text-red-400">*</span>
                    </label>
                    <div className="grid grid-cols-1 gap-2">
                      {REPORT_REASONS.map((r) => (
                        <label
                          key={r.code}
                          className={cn(
                            "flex cursor-pointer items-center gap-3 rounded-xl border px-4 py-3 text-sm transition-all",
                            reason === r.code
                              ? "border-cyan-500/50 bg-cyan-500/10 text-text-primary"
                              : "border-border-subtle bg-surface-muted text-text-secondary hover:border-border-focus hover:bg-surface-hover"
                          )}
                        >
                          <input
                            type="radio"
                            name="reason"
                            value={r.code}
                            checked={reason === r.code}
                            onChange={() => setReason(r.code)}
                            className="sr-only"
                          />
                          <span
                            className={cn(
                              "flex h-4 w-4 shrink-0 items-center justify-center rounded-full border",
                              reason === r.code
                                ? "border-cyan-400 bg-cyan-400"
                                : "border-text-muted"
                            )}
                          >
                            {reason === r.code && (
                              <span className="h-1.5 w-1.5 rounded-full bg-surface-base" />
                            )}
                          </span>
                          {r.label}
                        </label>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label htmlFor="details" className="mb-2 block text-sm font-medium text-text-primary">
                      Additional details{" "}
                      <span className="text-text-muted font-normal">(optional)</span>
                    </label>
                    <textarea
                      id="details"
                      rows={3}
                      value={details}
                      onChange={(e) => setDetails(e.target.value)}
                      placeholder="Provide any additional context that might help our review..."
                      className="w-full resize-none rounded-xl border border-border-subtle bg-surface-muted px-4 py-3 text-sm text-text-primary placeholder:text-text-muted focus:border-border-focus focus:outline-none focus:ring-2 focus:ring-cyan-500/20"
                    />
                  </div>

                  <div className="flex justify-end gap-3 pt-2">
                    <Button variant="ghost" type="button" onClick={handleClose}>
                      Cancel
                    </Button>
                    <Button type="submit" disabled={!reason || isSubmitting}>
                      {isSubmitting ? (
                        <>
                          <Loader2 className="h-4 w-4 animate-spin" />
                          Submitting&hellip;
                        </>
                      ) : (
                        "Submit report"
                      )}
                    </Button>
                  </div>
                </form>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
