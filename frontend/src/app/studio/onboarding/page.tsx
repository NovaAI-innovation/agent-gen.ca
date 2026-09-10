"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/authStore";
import { api } from "@/lib/api";
import { CreatorProfileForm } from "@/features/creators/CreatorProfileForm";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Alert } from "@/components/ui/Alert";

export default function OnboardingPage() {
  const { token, user } = useAuthStore();
  const router = useRouter();
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) {
      router.push("/");
      return;
    }

    const fetchProfile = async () => {
      try {
        const { data } = await api.get("/users/me/creator-profile");
        setProfile(data);
      } catch {
        // No profile yet
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [token, router]);

  if (!token) return null;
  if (loading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-action-primary/30 border-t-action-primary" />
      </div>
    );
  }

  const status = profile?.creator_status;

  return (
    <div className="mx-auto max-w-2xl px-4 py-12">
      <div className="mb-8 text-center">
        <h1 className="text-2xl font-bold text-text-primary">
          Become a Creator
        </h1>
        <p className="mt-2 text-sm text-text-secondary">
          Set up your creator profile to publish agent components on
          agent-gen.ca
        </p>
      </div>

      {user && (
        <div className="mb-6 flex items-center justify-center gap-3">
          <span className="text-sm text-text-muted">Status:</span>
          <StatusBadge
            status={
              status === "approved"
                ? "success"
                : status === "pending"
                  ? "pending"
                  : "info"
            }
          >
            {status === "none" || !status
              ? "Not submitted"
              : status === "pending"
                ? "Under review"
                : status === "approved"
                  ? "Approved"
                  : status === "rejected"
                    ? "Changes requested"
                    : status}
          </StatusBadge>
        </div>
      )}

      {status === "rejected" && profile?.reviewer_notes && (
        <Alert variant="danger" className="mb-6">
          <strong>Review notes:</strong> {profile.reviewer_notes}
        </Alert>
      )}

      <div className="rounded-2xl border border-border-subtle bg-surface-elevated p-6 shadow-sm">
        <CreatorProfileForm
          existing={profile}
          onComplete={() => {
            window.location.reload();
          }}
        />
      </div>
    </div>
  );
}