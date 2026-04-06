import { useState, useEffect, useCallback, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronRight, ChevronLeft, X, Brain, Crown, BarChart3, Activity, Beaker, FlaskConical, Bot, Radio } from "lucide-react";
import { Button } from "./ui/button";

const TOUR_KEY = "alphaTourSeen";

const steps = [
  {
    id: "welcome",
    title: "Welcome to My-AlphaAI",
    body: "Your AI-powered crypto signal intelligence platform. Let us show you around — it only takes 30 seconds.",
    target: null,
    icon: Brain,
    iconGradient: "from-[#7B61FF] to-[#00FF94]",
  },
  {
    id: "dashboard",
    title: "Your Command Center",
    body: "Real-time portfolio stats, signal counts, active agents, and recent alerts — all at a glance.",
    target: '[data-testid="app-nav-dashboard"]',
    icon: BarChart3,
  },
  {
    id: "signals",
    title: "Live Trading Signals",
    body: "Every signal includes an action (LONG/SHORT/CLOSE), confidence score, asset price, and the AI agent that generated it.",
    target: '[data-testid="app-nav-live-signals"]',
    icon: Activity,
  },
  {
    id: "research",
    title: "AI Research Engine",
    body: "Ask questions about any crypto asset and get AI-powered analysis backed by real market data.",
    target: '[data-testid="app-nav-research"]',
    icon: Beaker,
  },
  {
    id: "lab",
    title: "Strategy Lab",
    body: "Build and backtest your own trading strategies with historical data. No coding required.",
    target: '[data-testid="app-nav-strategy-lab"]',
    icon: FlaskConical,
  },
  {
    id: "agents",
    title: "4 AI Agents, 24/7",
    body: "Momentum Scanner, Sentiment Analyzer, Whale Tracker, and Volatility Engine — each specializing in a different signal type.",
    target: '[data-testid="app-nav-ai-agents"]',
    icon: Bot,
  },
  {
    id: "mode",
    title: "Demo Mode Active",
    body: "You're viewing simulated data right now. Upgrade to Pro to unlock real-time signals from all 4 agents.",
    target: '[data-testid="system-mode-badge"]',
    icon: Radio,
  },
  {
    id: "cta",
    title: "Ready to Go Live?",
    body: "Unlock unlimited real-time signals, copy trading, advanced analytics, and priority agent access with Pro.",
    target: null,
    icon: Crown,
    iconGradient: "from-[#FFB800] to-[#FF6B00]",
    isCTA: true,
  },
];

export default function GuidedTour() {
  const [active, setActive] = useState(false);
  const [step, setStep] = useState(0);
  const [spotRect, setSpotRect] = useState(null);
  const navigate = useNavigate();
  const rafRef = useRef(null);

  const current = steps[step];
  const isFirst = step === 0;
  const isLast = step === steps.length - 1;

  const measureTarget = useCallback(() => {
    if (!current?.target) { setSpotRect(null); return; }
    const el = document.querySelector(current.target);
    if (!el || el.offsetParent === null) { setSpotRect(null); return; }
    const r = el.getBoundingClientRect();
    const pad = 6;
    setSpotRect({
      top: r.top - pad,
      left: r.left - pad,
      width: r.width + pad * 2,
      height: r.height + pad * 2,
    });
  }, [current]);

  useEffect(() => {
    if (!active) return;
    measureTarget();
    const onResize = () => { cancelAnimationFrame(rafRef.current); rafRef.current = requestAnimationFrame(measureTarget); };
    window.addEventListener("resize", onResize);
    window.addEventListener("scroll", onResize, true);
    return () => {
      window.removeEventListener("resize", onResize);
      window.removeEventListener("scroll", onResize, true);
      cancelAnimationFrame(rafRef.current);
    };
  }, [active, step, measureTarget]);

  // Auto-start for new demo users
  useEffect(() => {
    if (localStorage.getItem(TOUR_KEY)) return;
    const t = setTimeout(() => setActive(true), 800);
    return () => clearTimeout(t);
  }, []);

  // Restart event listener
  useEffect(() => {
    const handler = () => { setStep(0); setActive(true); };
    window.addEventListener("alphaai-restart-tour", handler);
    return () => window.removeEventListener("alphaai-restart-tour", handler);
  }, []);

  const close = useCallback(() => {
    setActive(false);
    localStorage.setItem(TOUR_KEY, "true");
  }, []);

  const next = useCallback(() => {
    if (isLast) { close(); navigate("/pricing"); }
    else setStep(s => s + 1);
  }, [isLast, close, navigate]);

  const back = useCallback(() => {
    if (!isFirst) setStep(s => s - 1);
  }, [isFirst]);

  if (!active) return null;

  // Tooltip positioning
  const getTooltipStyle = () => {
    if (!spotRect) return null;
    const centerX = spotRect.left + spotRect.width / 2;
    const tooltipW = Math.min(360, window.innerWidth - 32);
    let left = Math.max(16, Math.min(centerX - tooltipW / 2, window.innerWidth - tooltipW - 16));
    let top = spotRect.top + spotRect.height + 16;
    let arrowDir = "top";
    if (top + 220 > window.innerHeight) {
      top = spotRect.top - 16;
      arrowDir = "bottom";
    }
    return { style: { position: "fixed", top, left, width: tooltipW, ...(arrowDir === "bottom" ? { transform: "translateY(-100%)" } : {}) }, arrowDir };
  };

  const tooltip = getTooltipStyle();
  const IconComp = current.icon;

  return (
    <AnimatePresence>
      <motion.div
        key="tour"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.25 }}
        className="fixed inset-0 z-[9999]"
        data-testid="guided-tour-overlay"
      >
        {/* Backdrop */}
        {spotRect ? (
          <div
            className="fixed pointer-events-none"
            style={{
              top: spotRect.top,
              left: spotRect.left,
              width: spotRect.width,
              height: spotRect.height,
              borderRadius: 10,
              boxShadow: "0 0 0 9999px rgba(0,0,0,0.82), 0 0 24px 2px rgba(123,97,255,0.35)",
              transition: "all 0.4s cubic-bezier(0.4,0,0.2,1)",
            }}
          />
        ) : (
          <div className="fixed inset-0 bg-black/85 backdrop-blur-sm" />
        )}

        {/* Click shield */}
        <div className="fixed inset-0" />

        {/* Tooltip */}
        <motion.div
          key={step}
          initial={{ opacity: 0, y: 10, scale: 0.97 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.28, ease: [0.4, 0, 0.2, 1] }}
          className={tooltip ? "" : "fixed inset-0 flex items-center justify-center p-4"}
          style={tooltip?.style || {}}
          data-testid={`tour-step-${current.id}`}
        >
          <div
            className={`relative bg-[#0D0D0D]/95 backdrop-blur-xl border border-zinc-800/60 rounded-2xl p-5 sm:p-6 ${tooltip ? "" : "max-w-sm w-full"}`}
            style={{ boxShadow: "0 0 48px rgba(123,97,255,0.12), 0 20px 40px rgba(0,0,0,0.6)" }}
          >
            {/* Arrow */}
            {tooltip && (
              <div
                className="absolute w-3 h-3 bg-[#0D0D0D]/95 border-zinc-800/60 rotate-45"
                style={
                  tooltip.arrowDir === "top"
                    ? { top: -6, left: "50%", marginLeft: -6, borderLeft: "1px solid", borderTop: "1px solid" }
                    : { bottom: -6, left: "50%", marginLeft: -6, borderRight: "1px solid", borderBottom: "1px solid" }
                }
              />
            )}

            {/* Close */}
            <button
              onClick={close}
              className="absolute top-3 right-3 p-1.5 rounded-lg text-zinc-600 hover:text-zinc-300 hover:bg-white/5 transition-colors"
              data-testid="tour-close-btn"
            >
              <X className="w-4 h-4" />
            </button>

            {/* Icon for center steps */}
            {!tooltip && IconComp && (
              <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${current.iconGradient || "from-[#7B61FF] to-[#00FF94]"} flex items-center justify-center mx-auto mb-4`}>
                <IconComp className="w-7 h-7 text-white" />
              </div>
            )}

            {/* Inline icon for spotlight steps */}
            {tooltip && IconComp && (
              <div className="flex items-center gap-2.5 mb-3">
                <div className="w-8 h-8 rounded-lg bg-[#7B61FF]/15 flex items-center justify-center shrink-0">
                  <IconComp className="w-4 h-4 text-[#7B61FF]" />
                </div>
                <h3 className="text-base font-bold text-white pr-6">{current.title}</h3>
              </div>
            )}

            {!tooltip && <h3 className="text-lg font-bold text-white mb-2 pr-6 text-center">{current.title}</h3>}

            <p className={`text-sm text-zinc-400 leading-relaxed mb-5 ${!tooltip ? "text-center" : ""}`}>{current.body}</p>

            {/* Step dots + controls */}
            <div className="flex items-center justify-between">
              <div className="flex gap-1.5">
                {steps.map((_, i) => (
                  <div
                    key={i}
                    className={`h-1.5 rounded-full transition-all duration-300 ${
                      i === step
                        ? "w-6 bg-gradient-to-r from-[#7B61FF] to-[#00FF94]"
                        : i < step
                        ? "w-1.5 bg-[#7B61FF]/50"
                        : "w-1.5 bg-zinc-700"
                    }`}
                  />
                ))}
              </div>
              <div className="flex items-center gap-2">
                {!isFirst && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={back}
                    className="rounded-full h-8 px-3 text-xs text-zinc-400 hover:text-white"
                    data-testid="tour-back-btn"
                  >
                    <ChevronLeft className="w-3.5 h-3.5 mr-0.5" />Back
                  </Button>
                )}
                {isFirst && (
                  <button onClick={close} className="text-xs text-zinc-500 hover:text-zinc-300 transition-colors px-2" data-testid="tour-skip-btn">
                    Skip tour
                  </button>
                )}
                <Button
                  size="sm"
                  onClick={next}
                  className={`rounded-full h-8 px-4 text-xs font-medium ${
                    current.isCTA
                      ? "bg-gradient-to-r from-[#FFB800] to-[#FF6B00] hover:opacity-90 text-black"
                      : "bg-[#7B61FF] hover:bg-[#7B61FF]/90 text-white"
                  }`}
                  data-testid="tour-next-btn"
                >
                  {current.isCTA ? "Upgrade to Pro" : isFirst ? <>Start Tour <ChevronRight className="w-3.5 h-3.5 ml-1" /></> : <>Next <ChevronRight className="w-3.5 h-3.5 ml-1" /></>}
                </Button>
              </div>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}

export const restartTour = () => {
  localStorage.removeItem(TOUR_KEY);
  window.dispatchEvent(new Event("alphaai-restart-tour"));
};
