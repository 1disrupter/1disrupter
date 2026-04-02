import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { TrendingUp, Layers, CreditCard, ArrowRight, X } from "lucide-react";
import { Button } from "./ui/button";

const ONBOARDING_KEY = "alphaai_onboarded";

const steps = [
  {
    icon: TrendingUp,
    title: "Welcome to AlphaAI",
    description: "Your AI-powered crypto trading signals platform. We analyze markets in real-time so you can make smarter decisions faster.",
    accent: "#7B61FF",
  },
  {
    icon: Layers,
    title: "How Signals Work",
    description: "Our strategies generate buy, hold, and sell signals based on technical analysis and AI models. Subscribe to strategies that match your risk profile and receive real-time alerts.",
    accent: "#00FF94",
  },
  {
    icon: CreditCard,
    title: "Flexible Subscriptions",
    description: "Browse the Strategy Marketplace, subscribe to any strategy for $9.99/mo, and manage everything from your Billing Portal. Cancel anytime — no lock-in.",
    accent: "#22d3ee",
  },
];

const OnboardingModal = () => {
  const [show, setShow] = useState(false);
  const [step, setStep] = useState(0);

  useEffect(() => {
    if (!localStorage.getItem(ONBOARDING_KEY)) {
      const timer = setTimeout(() => setShow(true), 1200);
      return () => clearTimeout(timer);
    }
  }, []);

  const finish = () => {
    localStorage.setItem(ONBOARDING_KEY, "true");
    setShow(false);
  };

  const next = () => {
    if (step < steps.length - 1) setStep(s => s + 1);
    else finish();
  };

  if (!show) return null;

  const current = steps[step];
  const Icon = current.icon;

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 z-[100] flex items-center justify-center px-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        data-testid="onboarding-modal"
      >
        {/* Backdrop */}
        <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" onClick={finish} />

        {/* Modal */}
        <motion.div
          className="relative w-full max-w-md bg-[#0f0f0f] border border-zinc-800 rounded-2xl overflow-hidden shadow-2xl"
          initial={{ scale: 0.9, opacity: 0, y: 20 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          exit={{ scale: 0.9, opacity: 0, y: 20 }}
          transition={{ type: "spring", damping: 25 }}
        >
          {/* Skip button */}
          <button
            onClick={finish}
            className="absolute top-4 right-4 text-zinc-600 hover:text-zinc-300 transition-colors z-10"
            data-testid="onboarding-skip"
          >
            <X className="w-5 h-5" />
          </button>

          {/* Top accent bar */}
          <motion.div
            className="h-1 w-full"
            style={{ background: current.accent }}
            layoutId="onboarding-accent"
          />

          <div className="p-8 pt-10">
            <AnimatePresence mode="wait">
              <motion.div
                key={step}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.25 }}
                className="text-center"
              >
                <div
                  className="w-14 h-14 rounded-xl mx-auto mb-5 flex items-center justify-center"
                  style={{ background: `${current.accent}15` }}
                >
                  <Icon className="w-7 h-7" style={{ color: current.accent }} />
                </div>

                <h2 className="text-xl font-bold font-['Outfit'] text-white mb-3" data-testid="onboarding-title">
                  {current.title}
                </h2>
                <p className="text-sm text-zinc-400 leading-relaxed">
                  {current.description}
                </p>
              </motion.div>
            </AnimatePresence>

            {/* Progress dots */}
            <div className="flex justify-center gap-2 mt-8 mb-6">
              {steps.map((_, i) => (
                <motion.div
                  key={i}
                  className="h-1.5 rounded-full transition-colors"
                  animate={{
                    width: i === step ? 24 : 8,
                    backgroundColor: i === step ? current.accent : "#333",
                  }}
                  data-testid={`onboarding-dot-${i}`}
                />
              ))}
            </div>

            {/* Actions */}
            <div className="flex items-center justify-between">
              <button
                onClick={finish}
                className="text-xs text-zinc-600 hover:text-zinc-400 transition-colors"
                data-testid="onboarding-skip-text"
              >
                Skip
              </button>
              <Button
                onClick={next}
                className="px-6 text-sm font-medium rounded-full"
                style={{ background: current.accent, color: "#000" }}
                data-testid="onboarding-next-btn"
              >
                {step === steps.length - 1 ? "Get Started" : "Next"}
                <ArrowRight className="w-4 h-4 ml-1" />
              </Button>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default OnboardingModal;
