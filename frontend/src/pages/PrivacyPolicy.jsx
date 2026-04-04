import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { ArrowLeft } from "lucide-react";

const PrivacyPolicy = () => {
  return (
    <div className="min-h-screen pt-28 pb-20 px-4" data-testid="privacy-page">
      <div className="max-w-3xl mx-auto">
        <Link to="/" className="inline-flex items-center gap-2 text-zinc-500 hover:text-white text-sm mb-8 transition-colors" data-testid="privacy-back-link">
          <ArrowLeft className="w-4 h-4" />Back to Home
        </Link>

        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
          <h1 className="text-3xl md:text-4xl font-bold font-['Outfit'] mb-2" data-testid="privacy-title">Privacy Policy</h1>
          <p className="text-zinc-500 text-sm mb-10">Last updated: April 4, 2026</p>

          <div className="space-y-8 text-zinc-400 text-sm leading-relaxed">
            <section>
              <h2 className="text-lg font-semibold text-white mb-3 font-['Outfit']">1. Information We Collect</h2>
              <p>When you register, we collect your email address, name, and hashed password. We do not store plaintext passwords. If you subscribe to a paid plan, Stripe processes your payment information — we never see or store your card details.</p>
            </section>

            <section>
              <h2 className="text-lg font-semibold text-white mb-3 font-['Outfit']">2. How We Use Your Information</h2>
              <p>We use your information to: (a) provide and maintain the Platform; (b) process subscriptions and payments; (c) send transactional emails (verification, password reset); (d) improve the Platform through anonymized analytics; (e) prevent fraud and abuse.</p>
            </section>

            <section>
              <h2 className="text-lg font-semibold text-white mb-3 font-['Outfit']">3. Analytics & Cookies</h2>
              <p>We use PostHog for product analytics to understand how users interact with the Platform. This includes page views, feature usage, and session data. We also use internal analytics to track API performance and service health. You may opt out of analytics cookies via the cookie consent banner.</p>
            </section>

            <section>
              <h2 className="text-lg font-semibold text-white mb-3 font-['Outfit']">4. Data Storage</h2>
              <p>Your data is stored in secure MongoDB databases. We implement industry-standard security measures including encryption at rest and in transit. Exchange API keys (if provided for testnet integration) are encrypted using Fernet symmetric encryption.</p>
            </section>

            <section>
              <h2 className="text-lg font-semibold text-white mb-3 font-['Outfit']">5. Third-Party Services</h2>
              <p>We integrate with the following third-party services:</p>
              <ul className="list-disc pl-6 mt-2 space-y-1">
                <li><span className="text-white">Stripe</span> — Payment processing (PCI DSS compliant)</li>
                <li><span className="text-white">PostHog</span> — Product analytics</li>
                <li><span className="text-white">Resend</span> — Transactional email delivery</li>
                <li><span className="text-white">Kraken / CoinGecko</span> — Market data (public APIs, no user data shared)</li>
              </ul>
            </section>

            <section>
              <h2 className="text-lg font-semibold text-white mb-3 font-['Outfit']">6. Data Retention</h2>
              <p>We retain your account data for as long as your account is active. If you request account deletion, we will remove your personal data within 30 days. Anonymized analytics data may be retained indefinitely.</p>
            </section>

            <section>
              <h2 className="text-lg font-semibold text-white mb-3 font-['Outfit']">7. Your Rights</h2>
              <p>You have the right to: (a) access your personal data; (b) correct inaccurate data; (c) request deletion of your data; (d) export your data in a portable format; (e) opt out of non-essential analytics. To exercise these rights, contact us at the email below.</p>
            </section>

            <section>
              <h2 className="text-lg font-semibold text-white mb-3 font-['Outfit']">8. Children's Privacy</h2>
              <p>The Platform is not intended for individuals under 18 years of age. We do not knowingly collect personal information from minors.</p>
            </section>

            <section>
              <h2 className="text-lg font-semibold text-white mb-3 font-['Outfit']">9. Changes to This Policy</h2>
              <p>We may update this Privacy Policy from time to time. Changes will be posted on this page with an updated date. We encourage you to review this page periodically.</p>
            </section>

            <section>
              <h2 className="text-lg font-semibold text-white mb-3 font-['Outfit']">10. Contact</h2>
              <p>For privacy-related inquiries, contact us at <span className="text-[#7B61FF]">privacy@my-alpha-ai.com</span>.</p>
            </section>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default PrivacyPolicy;
