"use client";

import { useState } from "react";
import { useAuthStore } from "@/store/authStore";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { Field } from "@/components/ui/Field";
import { Alert } from "@/components/ui/Alert";

interface CreatorProfile {
  handle: string;
  display_name: string;
  bio: string;
  support_link: string;
  payout_address: string;
  terms_accepted: boolean;
  creator_status: string;
}

interface Props {
  existing?: CreatorProfile | null;
  onComplete: () => void;
}

export function CreatorProfileForm({ existing, onComplete }: Props) {
  const { setUser } = useAuthStore();
  const [handle, setHandle] = useState(existing?.handle ?? "");
  const [displayName, setDisplayName] = useState(existing?.display_name ?? "");
  const [bio, setBio] = useState(existing?.bio ?? "");
  const [supportLink, setSupportLink] = useState(existing?.support_link ?? "");
  const [payoutAddress, setPayoutAddress] = useState(existing?.payout_address ?? "");
  const [termsAccepted, setTermsAccepted] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isSubmitted = existing?.creator_status === "pending";
  const isApproved = existing?.creator_status === "approved";

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!handle.trim()) {
      setError("Handle is required");
      return;
    }
    if (!displayName.trim()) {
      setError("Display name is required");
      return;
    }
    if (!termsAccepted) {
      setError("You must accept the terms");
      return;
    }

    setSubmitting(true);
    try {
      const { data } = await api.post("/users/me/creator-profile", {
        handle: handle.trim(),
        display_name: displayName.trim(),
        bio: bio.trim(),
        support_link: supportLink.trim() || null,
        payout_address: payoutAddress.trim() || null,
        terms_accepted: termsAccepted,
      });

      // Sync updated user state
      setUser(data);
      onComplete();
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ?? "Failed to submit creator profile"
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && <Alert variant="danger">{error}</Alert>}

      {isApproved && (
        <Alert variant="success">You are an approved creator!</Alert>
      )}
      {isSubmitted && (
        <Alert variant="info">
          Your application is pending review. You can update your profile
          while waiting.
        </Alert>
      )}

      <div className="grid gap-5 sm:grid-cols-2">
        <Field id="handle" label="Handle" hint="Unique URL identifier" required>
          <input
            type="text"
            value={handle}
            onChange={(e) => setHandle(e.target.value)}
            placeholder="my-agent-handle"
            maxLength={30}
            className="w-full rounded-lg border border-border-subtle bg-surface-muted px-3 py-2 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-action-primary/50"
            required
          />
        </Field>

        <Field id="display_name" label="Display Name" required>
          <input
            type="text"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            placeholder="My Agent Studio"
            maxLength={60}
            className="w-full rounded-lg border border-border-subtle bg-surface-muted px-3 py-2 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-action-primary/50"
            required
          />
        </Field>
      </div>

      <Field id="bio" label="Bio" hint="Tell the community about yourself">
        <textarea
          value={bio}
          onChange={(e) => setBio(e.target.value)}
          placeholder="Agent developer passionate about..."
          rows={3}
          className="w-full rounded-lg border border-border-subtle bg-surface-muted px-3 py-2 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-action-primary/50"
        />
      </Field>

      <div className="grid gap-5 sm:grid-cols-2">
        <Field id="support_link" label="Support Link" hint="GitHub, Discord, or website">
          <input
            type="url"
            value={supportLink}
            onChange={(e) => setSupportLink(e.target.value)}
            placeholder="https://github.com/..."
            className="w-full rounded-lg border border-border-subtle bg-surface-muted px-3 py-2 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-action-primary/50"
          />
        </Field>

        <Field id="payout_address" label="Payout Address" hint="Solana wallet for earnings">
          <input
            type="text"
            value={payoutAddress}
            onChange={(e) => setPayoutAddress(e.target.value)}
            placeholder="6hc7FwQFqBaFpKz..."
            maxLength={44}
            className="w-full rounded-lg border border-border-subtle bg-surface-muted px-3 py-2 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-action-primary/50"
          />
        </Field>
      </div>

      <label className="flex items-start gap-3">
        <input
          type="checkbox"
          checked={termsAccepted}
          onChange={(e) => setTermsAccepted(e.target.checked)}
          className="mt-1 h-4 w-4 rounded border-border-subtle text-action-primary focus:ring-action-primary/50"
          required
        />
        <span className="text-sm text-text-secondary">
          I agree to the{" "}
          <a href="/terms" className="text-action-primary underline">
            Creator Terms of Service
          </a>{" "}
          and confirm that I will not publish harmful, plagiarized, or
          malicious agent components.
        </span>
      </label>

      <Button type="submit" loading={submitting} className="w-full sm:w-auto">
        {isSubmitted ? "Update Profile" : "Submit for Review"}
      </Button>
    </form>
  );
}