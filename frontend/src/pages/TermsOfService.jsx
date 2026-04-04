import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { ArrowLeft } from "lucide-react";

export default function TermsOfService() {
  return (
    <div className="min-h-screen pt-28 pb-20 px-4" data-testid="terms-page">
      <div className="max-w-3xl mx-auto">
        <Link to="/" className="inline-flex items-center gap-2 text-zinc-500 hover:text-white text-sm mb-8 transition-colors" data-testid="terms-back-link">
          <ArrowLeft className="w-4 h-4" />Back to Home
        </Link>

        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
          <h1 className="text-3xl md:text-4xl font-bold font-['Outfit'] mb-2" data-testid="terms-title">Terms of Service</h1>
          <p className="text-zinc-500 text-sm mb-10">Last updated: April 2026</p>

          <div className="space-y-8 text-zinc-400 text-sm leading-relaxed">
            <section>
              <h2 className="text-lg font-semibold text-white mb-3 font-['Outfit']">1. Overview</h2>
              <p>Alpha AI provides AI-powered crypto strategy analytics, signals, and tools. By using this platform, you agree to these Terms.</p>
            </section>

            <section>
              <h2 className="text-lg font-semibold text-white mb-3 font-['Outfit']">2. Not Financial Advice</h2>
              <p>Alpha AI does not provide financial, investment, or trading advice. All signals and analytics are for informational purposes only.</p>
            </section>

            <section>
              <h2 className="text-lg font-semibold text-white mb-3 font-['Outfit']">3. User Responsibilities</h2>
              <p>You are responsible for your trading decisions and for complying with applicable laws in your jurisdiction.</p>
            </section>

            <section>
              <h2 className="text-lg font-semibold text-white mb-3 font-['Outfit']">4. Subscriptions</h2>
              <p>Paid plans are billed via Stripe. You may cancel anytime via the Billing Portal.</p>
            </section>

            <section>
              <h2 className="text-lg font-semibold text-white mb-3 font-['Outfit']">5. Limitation of Liability</h2>
              <p>Alpha AI is not liable for losses, damages, or trading outcomes.</p>
            </section>

            <section>
              <h2 className="text-lg font-semibold text-white mb-3 font-['Outfit']">6. Contact</h2>
              <p>Email: <span className="text-[#7B61FF]">support@my-alpha-ai.com</span></p>
            </section>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
