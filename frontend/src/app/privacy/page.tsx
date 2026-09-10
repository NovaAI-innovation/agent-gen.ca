import type { Metadata } from "next";
import { AppShell } from "@/components/templates/AppShell";

export const metadata: Metadata = {
  title: "Privacy Policy — agent-gen.ca",
  description: "How agent-gen.ca collects, uses, and protects your information.",
};

export default function PrivacyPage() {
  return (
    <AppShell contentClassName="max-w-3xl">
      <article className="prose prose-invert prose-cyan max-w-none">
        <h1>Privacy Policy</h1>
        <p className="lead text-text-secondary">
          Last updated: September 2026. This policy describes how agent-gen.ca handles your data.
        </p>

        <h2>1. Information We Collect</h2>
        <p>
          <strong>Wallet address.</strong> Your Solana public key is stored to authenticate your account and associate
          it with your listings and purchases. This is public by nature on the Solana blockchain.
        </p>
        <p>
          <strong>Listing content.</strong> Titles, descriptions, tags, configuration data, and pricing you submit are
          stored and made publicly visible on the marketplace.
        </p>
        <p>
          <strong>Usage data.</strong> We may collect basic analytics on how the marketplace is used, such as page
          views and download counts. This data is aggregated and anonymized where possible.
        </p>
        <p>
          <strong>Communications.</strong> If you contact us, we store the content of your message.
        </p>

        <h2>2. How We Use Information</h2>
        <ul>
          <li>To operate the marketplace and display listings</li>
          <li>To associate listings and reviews with your wallet</li>
          <li>To detect and prevent fraud or violations of our Terms</li>
          <li>To respond to your support requests</li>
          <li>To send transactional notifications (e.g., moderation decisions)</li>
        </ul>

        <h2>3. Data Retention</h2>
        <p>
          Listing and review data is retained indefinitely as it constitutes the public record of the marketplace.
          Wallet-based accounts cannot be deleted without removing associated listings. Contact us to request the
          removal of specific content in exceptional circumstances.
        </p>

        <h2>4. Data Sharing</h2>
        <p>
          We do not sell your personal data. Public listing data is visible to all visitors. Blockchain transactions
          involving SOL transfers are visible on the Solana ledger and are not controlled by us.
        </p>

        <h2>5. Security</h2>
        <p>
          We use standard industry measures to protect our infrastructure. Wallet-based authentication means the
          Service never holds your private keys. You are responsible for securing your own wallet credentials.
        </p>

        <h2>6. Cookies</h2>
        <p>
          The Service may use session cookies for authentication and preference storage. We do not use third-party
          advertising cookies.
        </p>

        <h2>7. Your Rights</h2>
        <p>
          Because authentication is wallet-based and listings are public content, you have limited ability to exercise
          data rights in the traditional sense. You may contact us to request removal of specific content or to
          report security concerns.
        </p>

        <h2>8. Children</h2>
        <p>
          The Service is not intended for users under the legal age in their jurisdiction. We do not knowingly
          collect data from minors.
        </p>

        <h2>9. Changes to This Policy</h2>
        <p>
          We may update this policy at any time. Material changes will be communicated via the Service&rsquo;s
          announcement channels. Continued use after changes constitutes acceptance.
        </p>

        <h2>10. Contact</h2>
        <p>
          For privacy concerns, please open an issue on the GitHub repository.
        </p>
      </article>
    </AppShell>
  );
}
