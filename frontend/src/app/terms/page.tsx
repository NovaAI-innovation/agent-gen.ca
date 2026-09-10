import type { Metadata } from "next";
import { AppShell } from "@/components/templates/AppShell";

export const metadata: Metadata = {
  title: "Terms of Service — agent-gen.ca",
  description: "Terms and conditions for using the agent-gen.ca marketplace.",
};

export default function TermsPage() {
  return (
    <AppShell contentClassName="max-w-3xl">
      <article className="prose prose-invert prose-cyan max-w-none">
        <h1>Terms of Service</h1>
        <p className="lead text-text-secondary">
          Last updated: September 2026. By accessing or using agent-gen.ca, you agree to be bound by these terms.
        </p>

        <h2>1. Acceptance of Terms</h2>
        <p>
          By accessing and using the agent-gen.ca marketplace (&ldquo;Service&rdquo;), you agree to comply with and be bound
          by these Terms of Service (&ldquo;Terms&rdquo;). If you do not agree to these Terms, do not use the Service.
        </p>

        <h2>2. Eligibility</h2>
        <p>
          You must have a valid Solana wallet to use the Service. You represent that you are of legal age and have the
          capacity to enter into binding agreements. You are responsible for all activity under your wallet.
        </p>

        <h2>3. Listings and Purchases</h2>
        <p>
          Sellers are solely responsible for the accuracy of their listings, including descriptions, pricing, and the
          content of digital goods offered. All transactions occur on-chain via Solana. agent-gen.ca does not process
          payments directly and is not a party to transactions between buyers and sellers.
        </p>
        <p>
          Purchases of digital goods are final and non-refundable unless a seller independently offers a refund policy.
          Disputes between buyers and sellers should be resolved directly; agent-gen.ca may intervene in cases of fraud.
        </p>

        <h2>4. Content Standards</h2>
        <p>
          Creators must only publish content they have the right to distribute. Prohibited content includes but is not
          limited to: malware, phishing tools, content that infringes intellectual property rights, and material that
          violates applicable law. We reserve the right to remove listings at our discretion.
        </p>

        <h2>5. Intellectual Property</h2>
        <p>
          Each listing&rsquo;s intellectual property remains with the original creator unless explicitly transferred. The
          Service retains no ownership over user-submitted content beyond what is necessary to operate the marketplace.
        </p>

        <h2>6. Disclaimers</h2>
        <p>
          The Service is provided &ldquo;as is&rdquo; and &ldquo;as available&rdquo; without warranties of any kind,
          express or implied. We do not guarantee that listings are free from defects, that the Service will be
          uninterrupted, or that any listing meets your specific requirements.
        </p>

        <h2>7. Limitation of Liability</h2>
        <p>
          To the maximum extent permitted by law, agent-gen.ca and its operators shall not be liable for any indirect,
          incidental, special, consequential, or punitive damages arising from your use of the Service.
        </p>

        <h2>8. Modifications</h2>
        <p>
          We may revise these Terms at any time by posting an updated version on this page. Continued use of the Service
          after changes constitutes acceptance of the revised Terms.
        </p>

        <h2>9. Governing Law</h2>
        <p>
          These Terms are governed by applicable law. Any disputes arising from these Terms shall be resolved in the
          courts of the relevant jurisdiction.
        </p>

        <h2>10. Contact</h2>
        <p>
          Questions about these Terms can be directed to the project maintainers via the GitHub repository.
        </p>
      </article>
    </AppShell>
  );
}
