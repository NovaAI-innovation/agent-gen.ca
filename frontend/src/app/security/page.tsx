import type { Metadata } from "next";
import { AppShell } from "@/components/templates/AppShell";

export const metadata: Metadata = {
  title: "Security Policy — agent-gen.ca",
  description: "How we handle security, how to report vulnerabilities, and security best practices for users.",
};

export default function SecurityPage() {
  return (
    <AppShell contentClassName="max-w-3xl">
      <article className="prose prose-invert prose-cyan max-w-none">
        <h1>Security Policy</h1>
        <p className="lead text-text-secondary">
          Last updated: September 2026.
        </p>

        <h2>1. Scope</h2>
        <p>
          This policy covers the agent-gen.ca marketplace application, its API, and associated infrastructure.
          It does not cover the broader Solana blockchain or third-party wallets.
        </p>

        <h2>2. Authentication</h2>
        <p>
          The Service uses wallet-based Sign-In With Ethereum (SIWF) adapted for Solana. Your private keys never
          leave your wallet and are never transmitted to our servers. We store only the public wallet address and
          a server-side nonce for the authentication handshake.
        </p>
        <p>
          Session tokens (JWT) are issued after successful signature verification and expire after 24 hours.
          Tokens must be stored securely by clients.
        </p>

        <h2>3. Data Protection</h2>
        <p>
          Sensitive data in transit is protected by TLS. Database credentials and secrets are managed through
          environment variables and are never committed to source code. We follow the principle of least
          privilege for all service accounts.
        </p>

        <h2>4. Listing Content</h2>
        <p>
          Downloadable artifacts submitted by creators are stored with integrity checksums. We recommend
          reviewing all downloaded code before execution, regardless of source.
        </p>

        <h2>5. Moderation and Fraud Detection</h2>
        <p>
          All new listings enter a moderation queue before becoming publicly visible. We monitor for
          anomalous behavior including coordinated fake reviews, price manipulation, and suspicious
          transaction patterns.
        </p>

        <h2>6. Vulnerability Disclosure</h2>
        <p>
          We welcome responsible disclosure of security vulnerabilities. If you discover a security issue,
          please:
        </p>
        <ol>
          <li>Do not disclose the issue publicly until we have had reasonable time to address it.</li>
          <li>Report it via the GitHub repository&rsquo;s Security tab or as a private issue.</li>
          <li>Include a clear description of the issue and, if possible, steps to reproduce it.</li>
        </ol>
        <p>
          We aim to acknowledge reports within 48 hours and to resolve critical issues within 14 days.
        </p>

        <h2>7. User Responsibilities</h2>
        <p>
          You are responsible for keeping your wallet credentials secure, using a reputable wallet provider,
          and verifying listings before downloading or purchasing. agent-gen.ca cannot recover funds
          sent to incorrect addresses or resolve disputes arising from user negligence.
        </p>

        <h2>8. Incident Response</h2>
        <p>
          In the event of a confirmed security incident, we will notify affected users via the contact
          information on file and post a summary on our communications channels within 72 hours of
          confirmation.
        </p>

        <h2>9. Third-Party Services</h2>
        <p>
          The Service depends on Railway for hosting and PostgreSQL. Security for these services is governed
          by their respective policies. The Solana blockchain itself is outside our security scope.
        </p>

        <h2>10. Policy Updates</h2>
        <p>
          We may update this policy as the Service evolves. Material changes will be noted on this page.
        </p>
      </article>
    </AppShell>
  );
}
