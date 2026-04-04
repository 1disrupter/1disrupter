import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { ArrowLeft } from "lucide-react";

export default function PrivacyPolicy() {
  return (
    <div className="min-h-screen pt-28 pb-20 px-4" data-testid="privacy-page">
      <div className="max-w-3xl mx-auto">
        <Link to="/" className="inline-flex items-center gap-2 text-zinc-500 hover:text-white text-sm mb-8 transition-colors" data-testid="privacy-back-link">
          <ArrowLeft className="w-4 h-4" />Back to Home
        </Link>

        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
          <h1 className="text-3xl md:text-4xl font-bold font-['Outfit'] mb-2" data-testid="privacy-title">Privacy Policy</h1>
          <p className="text-zinc-500 text-sm mb-10">Last updated: April 2026</p>

          <div className="space-y-8 text-zinc-400 text-sm leading-relaxed">
            <section>
              <h2 className="text-lg font-semibold text-white mb-3 font-['Outfit']">1. Data We Collect</h2>
              <p>We collect account information, usage analytics (via PostHog), and subscription data (via Stripe).</p>
            </section>

            <section>
              <h2 className="text-lg font-semibold text-white mb-3 font-['Outfit']">2. Cookies</h2>
              <p>We use cookies for analytics and improving user experience. You may accept or reject cookies via the consent banner.</p>
            </section>

            <section>
              <h2 className="text-lg font-semibold text-white mb-3 font-['Outfit']">3. How We Use Data</h2>
              <p>To operate the platform, improve features, and provide customer support.</p>
            </section>

            <section>
              <h2 className="text-lg font-semibold text-white mb-3 font-['Outfit']">4. Third-Party Services</h2>
              <p>Stripe, PostHog, and cloud hosting providers may process data.</p>
            </section>

            <section>
              <h2 className="text-lg font-semibold text-white mb-3 font-['Outfit']">5. Your Rights</h2>
              <p>You may request data deletion or export by contacting support.</p>
            </section>

            <section>
              <h2 className="text-lg font-semibold text-white mb-3 font-['Outfit']">6. Contact</h2>
              <p>Email: <span className="text-[#7B61FF]">privacy@my-alpha-ai.com</span></p>
            </section>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
