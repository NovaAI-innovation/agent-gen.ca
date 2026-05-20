import { PenSquare } from "lucide-react";
import { PublishWizard } from "./PublishWizard";
import { ContentTemplate } from "@/components/templates/ContentTemplate";

export const metadata = { title: "Publish - agent-gen.ca" };

export default function PublishPage() {
  return (
    <ContentTemplate
      maxWidthClassName="max-w-3xl"
      header={{
        icon: PenSquare,
        eyebrow: "Create",
        title: "Publish a listing",
        subtitle:
          "Share MCP servers, skills, agents, or packs with wallet-verified provenance and monetization-ready metadata.",
        accentClassName: "text-action-primary",
        stats: [
          { label: "Flow", value: "2-step guided" },
          { label: "Settlement", value: "SOL-native" },
        ],
      }}
    >
      <PublishWizard />
    </ContentTemplate>
  );
}
