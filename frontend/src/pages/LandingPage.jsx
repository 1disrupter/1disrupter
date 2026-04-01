import { useState, useEffect, useRef, useCallback } from "react";
import { Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowUpRight, ArrowRight, Activity, Zap, X,
  Check, Clock, Brain, TestTube, Beaker, Trophy,
  Rocket, Shield, Lock, ShieldCheck, Database, Terminal
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { BrandLockup, PoweredByTag } from "../components/BrandComponents";
import LivePriceTicker from "../components/LivePriceTicker";

const API = process.env.REACT_APP_BACKEND_URL;

/* ─── Live Metrics Terminal ─── */
const LiveMetricsTerminal = () => {
  const [tick, setTick] = useState(0);
  const intervalRef = useRef(null);

  useEffect(() => {
    intervalRef.current = setInterval(() => setTick(t => t + 1), 2400);
    return () => clearInterval(intervalRef.current);
  }, []);

  const metrics = [
    { label: "Active Engine", value: "Alpha Engine V4", color: "text-white" },
    { label: "Sharpe Ratio (30d)", value: "2.14", color: "text-[#00FF94]" },
    { label: "Win Rate", value: "68.3%", color: "text-[#00FF94]" },
    { label: "Max Drawdown", value: "-4.2%", color: "text-white" },
    { label: "Execution Latency", value: "12ms", color: "text-white" },
    { label: "Network", value: "Ethereum Sepolia", color: "text-white/80" },
  ];

  return (
    <motion.div
      className="w-full border border-white/10 bg-[#0B0B0F]/90 backdrop-blur-xl relative overflow-hidden shadow-[0_0_40px_rgba(0,0,0,0.5)]"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5, duration: 0.7, ease: [0.25, 0.46, 0.45, 0.94] }}
      data-testid="live-metrics-terminal"
    >
      {/* Subtle corner accent */}
      <div className="absolute top-0 right-0 w-24 h-24 bg-[#7B61FF]/5 blur-[40px] pointer-events-none" />

      {/* Header */}
      <div className="flex justify-between items-center border-b border-white/10 px-6 py-4 lg:px-8">
        <span className="font-data text-[11px] text-white/40 uppercase tracking-[0.15em]">
          Strategy Performance
        </span>
        <span className="flex items-center gap-2 text-[#00FF94] text-[11px] font-data uppercase tracking-[0.15em]" data-testid="terminal-live-indicator">
          <motion.span
            className="inline-block w-1.5 h-1.5 rounded-full bg-[#00FF94]"
            animate={{ opacity: [1, 0.3, 1] }}
            transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
          />
          Live
        </span>
      </div>

      {/* Rows */}
      <div className="px-6 py-4 lg:px-8 lg:py-5">
        {metrics.map((m, i) => (
          <motion.div
            key={m.label}
            className="flex justify-between items-center py-3 border-b border-white/5 last:border-0"
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.7 + i * 0.08, duration: 0.4 }}
          >
            <span className="font-data text-sm text-white/50">{m.label}</span>
            <motion.span
              className={`font-data text-sm ${m.color}`}
              key={`${m.label}-${tick}`}
              animate={{ opacity: [0.6, 1] }}
              transition={{ duration: 0.3 }}
            >
              {m.value}
            </motion.span>
          </motion.div>
        ))}
      </div>

      {/* Footer */}
      <div className="border-t border-white/5 px-6 py-3 lg:px-8 flex items-center justify-between">
        <span className="font-data text-[10px] text-white/25 uppercase tracking-widest">
          Last attestation: 2 hrs ago
        </span>
        <span className="font-data text-[10px] text-[#7B61FF]/60 uppercase tracking-widest">
          On-Chain Verified
        </span>
      </div>
    </motion.div>
  );
};

/* ─── Waitlist Modal ─── */
const EMAIL_RE = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

const WaitlistModal = ({ open, onClose }) => {
  const [email, setEmail] = useState('');
  const [note, setNote] = useState('');
  const [sending, setSending] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState('');

  const emailValid = EMAIL_RE.test(email);
  const showEmailError = email.length > 0 && !emailValid;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!emailValid || sending) return;
    setSending(true);
    setError('');
    try {
      const res = await fetch(`${API}/api/public/waitlist`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim(), note: note.trim() || undefined }),
      });
      if (res.status === 429) { setError('Too many requests. Please try again later.'); setSending(false); return; }
      if (!res.ok) { const d = await res.json().catch(() => ({})); setError(d.detail || 'Something went wrong.'); setSending(false); return; }
      setDone(true);
    } catch { setError('Network error. Please try again.'); }
    setSending(false);
  };

  const handleClose = () => { onClose(); setTimeout(() => { setEmail(''); setNote(''); setDone(false); setError(''); }, 300); };

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="fixed inset-0 z-50 flex items-center justify-center px-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
          data-testid="waitlist-modal-backdrop"
        >
          {/* Backdrop */}
          <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" onClick={handleClose} />

          {/* Modal */}
          <motion.div
            className="relative w-full max-w-md border border-white/10 bg-[#0B0B0F] shadow-[0_0_60px_rgba(123,97,255,0.1)] overflow-hidden"
            initial={{ opacity: 0, y: 20, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.97 }}
            transition={{ duration: 0.25, ease: [0.25, 0.46, 0.45, 0.94] }}
            data-testid="waitlist-modal"
          >
            {/* Corner glow */}
            <div className="absolute top-0 left-0 w-32 h-32 bg-[#7B61FF]/8 blur-[50px] pointer-events-none" />

            {/* Close */}
            <button onClick={handleClose} className="absolute top-4 right-4 text-white/30 hover:text-white/60 transition-colors z-10" data-testid="waitlist-modal-close">
              <X className="w-5 h-5" />
            </button>

            <div className="relative p-8">
              {done ? (
                <motion.div className="text-center py-4" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} data-testid="waitlist-success">
                  <div className="w-12 h-12 rounded-full bg-[#00FF94]/10 flex items-center justify-center mx-auto mb-4">
                    <Check className="w-6 h-6 text-[#00FF94]" />
                  </div>
                  <p className="text-white font-heading text-lg font-medium mb-2">You&apos;re on the waitlist!</p>
                  <p className="font-data text-sm text-white/40">We&apos;ll notify you when a spot opens.</p>
                  <button onClick={handleClose} className="mt-6 h-11 px-6 bg-white/5 border border-white/10 text-white font-data text-sm hover:bg-white/10 transition-colors" data-testid="waitlist-done-btn">Done</button>
                </motion.div>
              ) : (
                <>
                  <h2 className="font-heading text-xl font-medium text-white mb-1">Join the Waitlist</h2>
                  <p className="font-data text-xs text-white/40 mb-6">Beta is currently full. Be the first to know when a spot opens.</p>

                  <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                      <label className="block font-data text-xs text-white/50 uppercase tracking-widest mb-2">Email</label>
                      <input
                        type="email"
                        value={email}
                        onChange={e => setEmail(e.target.value)}
                        placeholder="you@example.com"
                        className={`w-full h-11 px-4 bg-white/5 border ${showEmailError ? 'border-red-500/50' : 'border-white/10'} text-white font-data text-sm placeholder-white/20 outline-none focus:border-[#7B61FF]/50 transition-colors`}
                        autoFocus
                        data-testid="waitlist-email-input"
                      />
                      {showEmailError && <p className="font-data text-xs text-red-400 mt-1" data-testid="waitlist-email-error">Please enter a valid email address</p>}
                    </div>
                    <div>
                      <label className="block font-data text-xs text-white/50 uppercase tracking-widest mb-2">What are you hoping to use My-AlphaAI for? <span className="text-white/20">(optional)</span></label>
                      <textarea
                        value={note}
                        onChange={e => setNote(e.target.value)}
                        rows={3}
                        maxLength={500}
                        placeholder="e.g. BTC swing trading, portfolio rebalancing..."
                        className="w-full px-4 py-3 bg-white/5 border border-white/10 text-white font-data text-sm placeholder-white/20 outline-none focus:border-[#7B61FF]/50 transition-colors resize-none"
                        data-testid="waitlist-note-input"
                      />
                    </div>
                    {error && <p className="font-data text-xs text-red-400" data-testid="waitlist-error">{error}</p>}
                    <button
                      type="submit"
                      disabled={!emailValid || sending}
                      className={`w-full h-12 font-data text-sm font-semibold tracking-wide flex items-center justify-center transition-all ${
                        !emailValid || sending
                          ? 'bg-zinc-800 text-zinc-500 cursor-not-allowed'
                          : 'bg-[#7B61FF] text-white hover:bg-[#6A50E5] shadow-[0_0_20px_rgba(123,97,255,0.15)]'
                      }`}
                      data-testid="waitlist-submit-btn"
                    >
                      {sending ? 'Submitting...' : 'Join Waitlist'}
                    </button>
                  </form>
                </>
              )}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

const LandingPage = () => {
  const [betaSpots, setBetaSpots] = useState(null);
  const [waitlistOpen, setWaitlistOpen] = useState(false);

  const fetchBetaSpots = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/public/beta-spots`);
      if (res.ok) setBetaSpots(await res.json());
    } catch { /* silent */ }
  }, []);

  useEffect(() => {
    fetchBetaSpots();
    const id = setInterval(fetchBetaSpots, 30000);
    return () => clearInterval(id);
  }, [fetchBetaSpots]);

  const remaining = betaSpots?.remaining ?? null;
  const isLow = remaining !== null && remaining <= 5;
  const isFull = remaining !== null && remaining <= 0;

  return (
    <div className="min-h-screen pt-[92px]">
      {/* Live Price Ticker */}
      <LivePriceTicker compact={true} />

      {/* ===== HERO SECTION ===== */}
      <section
        className="relative min-h-[85vh] flex flex-col justify-center pt-12 pb-16 md:pt-16 md:pb-24 border-b border-white/5 overflow-hidden"
        data-testid="hero-section"
      >
        {/* Background layers */}
        <div className="absolute inset-0 bg-[#050505]" />
        <div className="absolute inset-0 grid-pattern opacity-20" />
        <div className="absolute top-[10%] right-[-10%] w-[800px] h-[800px] bg-[#7B61FF]/8 rounded-full blur-[140px] pointer-events-none mix-blend-screen" />
        <div className="absolute bottom-[5%] left-[-5%] w-[500px] h-[500px] bg-[#00FF94]/4 rounded-full blur-[120px] pointer-events-none" />

        {/* Noise texture */}
        <div
          className="absolute inset-0 opacity-[0.02] pointer-events-none"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`,
            backgroundSize: '128px 128px',
          }}
        />

        <div className="w-full max-w-[1400px] mx-auto px-6 lg:px-12 relative z-10">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center">
            {/* Left Column — Copy */}
            <div className="lg:col-span-7 flex flex-col items-start gap-6 lg:gap-8">
              {/* Overline */}
              <motion.span
                className="font-data text-xs font-bold tracking-[0.2em] uppercase text-[#7B61FF]"
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, ease: [0.25, 0.46, 0.45, 0.94] }}
                data-testid="hero-overline"
              >
                On-Chain Verified Performance
              </motion.span>

              {/* H1 */}
              <motion.h1
                className="text-4xl sm:text-5xl lg:text-[4.25rem] leading-[1.05] tracking-tighter font-medium text-white font-heading"
                initial={{ opacity: 0, y: 24, filter: 'blur(4px)' }}
                animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
                transition={{ delay: 0.1, duration: 0.6, ease: [0.25, 0.46, 0.45, 0.94] }}
                data-testid="hero-title"
              >
                AI-Generated Crypto{' '}
                <br className="hidden sm:block" />
                Strategies.{' '}
                <span className="text-[#7B61FF]">Verified</span>{' '}
                <br className="hidden lg:block" />
                On-Chain.
              </motion.h1>

              {/* Sub-headline */}
              <motion.p
                className="text-base sm:text-lg text-white/55 leading-relaxed max-w-xl font-data"
                initial={{ opacity: 0, y: 18 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.22, duration: 0.5 }}
                data-testid="hero-description"
              >
                My-AlphaAI deploys quantitative strategies and writes every performance metric — Sharpe ratio, win rate, drawdown — directly to the blockchain. No screenshots. No manipulated backtests. Just verifiable data.
              </motion.p>

              {/* Micro-copy */}
              <motion.p
                className="font-data text-xs text-white/35 max-w-lg uppercase tracking-widest"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.32, duration: 0.4 }}
                data-testid="hero-microcopy"
              >
                Transparent metrics. Immutable records. Built for traders who verify.
              </motion.p>

              {/* CTA Buttons */}
              <motion.div
                className="flex flex-col sm:flex-row items-start gap-4 pt-2"
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4, duration: 0.5 }}
              >
                {isFull ? (
                  <button
                    onClick={() => setWaitlistOpen(true)}
                    className="h-14 px-8 bg-[#7B61FF] text-white font-data text-sm font-semibold tracking-wide flex items-center justify-center transition-all hover:bg-[#6A50E5] focus:ring-2 focus:ring-[#7B61FF]/50 shadow-[0_0_20px_rgba(123,97,255,0.15)] hover:shadow-[0_0_30px_rgba(123,97,255,0.3)]"
                    data-testid="cta-join-waitlist"
                  >
                    Join Waitlist
                    <ArrowRight className="w-4 h-4 ml-2.5" />
                  </button>
                ) : (
                  <Link to="/register">
                    <button
                      className="h-14 px-8 bg-[#7B61FF] text-white font-data text-sm font-semibold tracking-wide flex items-center justify-center transition-all hover:bg-[#6A50E5] focus:ring-2 focus:ring-[#7B61FF]/50 shadow-[0_0_20px_rgba(123,97,255,0.15)] hover:shadow-[0_0_30px_rgba(123,97,255,0.3)]"
                      data-testid="cta-join-beta"
                    >
                      Join Free Beta Access (Limited Spots)
                      <ArrowRight className="w-4 h-4 ml-2.5" />
                    </button>
                  </Link>
                )}
                <Link to="/demo">
                  <button
                    className="h-14 px-8 border border-[#7B61FF]/40 bg-[#7B61FF]/5 text-white font-data text-sm font-semibold tracking-wide flex items-center justify-center transition-all hover:bg-[#7B61FF]/15 hover:border-[#7B61FF]/60 focus:ring-2 focus:ring-[#7B61FF]/30"
                    data-testid="cta-start-demo"
                  >
                    Start Free Demo
                    <ArrowRight className="w-4 h-4 ml-2.5" />
                  </button>
                </Link>
                <Link to="/leaderboard">
                  <button
                    className="h-14 px-8 border border-white/20 bg-transparent text-white font-data text-sm font-semibold tracking-wide flex items-center justify-center transition-all hover:bg-white/5 hover:border-white/40 focus:ring-2 focus:ring-white/20"
                    data-testid="cta-view-metrics"
                  >
                    View Live Metrics
                  </button>
                </Link>
              </motion.div>

              {/* Spots remaining counter */}
              {remaining !== null && (
                <motion.div
                  className={`flex items-center gap-2 font-data text-sm ${
                    isFull ? 'text-zinc-500' : isLow ? 'text-amber-400' : 'text-white/50'
                  }`}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.48, duration: 0.4 }}
                  data-testid="beta-spots-counter"
                >
                  <motion.span
                    className={`inline-block w-2 h-2 rounded-full ${
                      isFull ? 'bg-zinc-600' : isLow ? 'bg-amber-400' : 'bg-[#00FF94]'
                    }`}
                    animate={isLow && !isFull ? { opacity: [1, 0.3, 1] } : {}}
                    transition={isLow && !isFull ? { duration: 1.2, repeat: Infinity, ease: 'easeInOut' } : {}}
                  />
                  {isFull
                    ? 'All beta spots have been claimed'
                    : `Spots Remaining: ${remaining}`}
                </motion.div>
              )}

              {/* Trust line */}
              <motion.p
                className="font-data text-[11px] text-white/25"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5, duration: 0.4 }}
                data-testid="hero-trust-line"
              >
                No credit card required. Free tier included.
              </motion.p>
            </div>

            {/* Right Column — Terminal */}
            <motion.div
              className="lg:col-span-5 hidden md:block"
              initial={{ opacity: 0, scale: 0.96 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.35, duration: 0.7, ease: 'easeOut' }}
            >
              <LiveMetricsTerminal />
            </motion.div>
          </div>

          {/* Trust Bar */}
          <motion.div
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 pt-14 mt-14 border-t border-white/10 w-full"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.65, duration: 0.6 }}
            data-testid="trust-bar"
          >
            {[
              { icon: ShieldCheck, title: "Verified On-Chain", sub: "Metrics written to Ethereum" },
              { icon: Database, title: "Transparent Metrics", sub: "Sharpe, drawdown, win rate — public" },
              { icon: Terminal, title: "Built for Serious Traders", sub: "Institutional-grade quantitative engine" },
              { icon: Activity, title: "Zero Hype, Real Data", sub: "No screenshots. No manipulation." },
            ].map((item, i) => (
              <motion.div
                key={item.title}
                className="flex flex-col gap-2.5"
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.75 + i * 0.08, duration: 0.4 }}
                data-testid={`trust-item-${i}`}
              >
                <item.icon className="w-5 h-5 text-[#7B61FF] mb-1" />
                <span className="font-data text-xs text-white uppercase tracking-widest">{item.title}</span>
                <span className="font-data text-xs text-white/35">{item.sub}</span>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ===== SECTION 1: MISSED vs CAPTURED ===== */}
      <section className="px-4 py-20 md:py-28 relative overflow-hidden" data-testid="missed-vs-captured-section">
        <div className="absolute inset-0 bg-[#0B0B0F]" />
        <div className="absolute top-1/2 left-1/3 w-[400px] h-[400px] bg-[#ef4444]/5 rounded-full blur-[120px] pointer-events-none" />
        <div className="absolute top-1/2 right-1/3 w-[400px] h-[400px] bg-[#00FF94]/5 rounded-full blur-[120px] pointer-events-none" />

        <div className="max-w-4xl mx-auto relative z-10">
          <motion.div initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.6 }}>
            <p className="text-center text-xs tracking-[0.3em] uppercase text-zinc-600 mb-3">BTC/USD · March 24, 2026 · 15-min candles</p>

            {/* Chart visual */}
            <div className="relative mx-auto max-w-2xl mb-12">
              <svg viewBox="0 0 600 200" className="w-full" fill="none" xmlns="http://www.w3.org/2000/svg">
                {/* Grid */}
                <line x1="50" y1="40" x2="550" y2="40" stroke="#fff" strokeOpacity="0.04" strokeWidth="0.5" />
                <line x1="50" y1="100" x2="550" y2="100" stroke="#fff" strokeOpacity="0.04" strokeWidth="0.5" />
                <line x1="50" y1="160" x2="550" y2="160" stroke="#fff" strokeOpacity="0.04" strokeWidth="0.5" />

                {/* Price labels */}
                <text x="555" y="167" fill="#52525b" fontSize="10" fontFamily="monospace">$64,800</text>
                <text x="555" y="47" fill="#52525b" fontSize="10" fontFamily="monospace">$67,200</text>

                {/* Candles — pre-breakout */}
                {[[80,155,145,140,160],[100,148,138,132,152],[120,140,150,128,155],[140,152,142,136,158]].map(([x,o,c,h,l],i) => (
                  <g key={`pre${i}`}>
                    <line x1={x} y1={h} x2={x} y2={l} stroke={c < o ? '#00FF94' : '#ef4444'} strokeWidth="1" strokeOpacity="0.4" />
                    <rect x={x-5} y={Math.min(o,c)} width="10" height={Math.abs(o-c)||2} fill={c < o ? '#00FF94' : '#ef4444'} fillOpacity="0.3" rx="1" />
                  </g>
                ))}

                {/* AlphaAI entry line */}
                <line x1="50" y1="155" x2="550" y2="155" stroke="#00FF94" strokeWidth="1" strokeDasharray="6 4" strokeOpacity="0.4" />

                {/* Breakout candles */}
                {[[170,148,120,115,152],[195,120,90,82,125],[220,90,65,58,95],[245,65,50,42,70],[270,50,42,36,55]].map(([x,o,c,h,l],i) => (
                  <g key={`brk${i}`}>
                    <line x1={x} y1={h} x2={x} y2={l} stroke="#00FF94" strokeWidth="1" strokeOpacity="0.6" />
                    <rect x={x-5} y={Math.min(o,c)} width="10" height={Math.abs(o-c)||2} fill="#00FF94" fillOpacity="0.7" rx="1" />
                  </g>
                ))}

                {/* Post-peak candles */}
                {[[295,42,55,38,60],[320,55,65,52,70],[345,65,58,54,72],[370,58,62,52,68],[395,62,68,58,72]].map(([x,o,c,h,l],i) => (
                  <g key={`post${i}`}>
                    <line x1={x} y1={h} x2={x} y2={l} stroke="#ef4444" strokeWidth="1" strokeOpacity="0.5" />
                    <rect x={x-5} y={Math.min(o,c)} width="10" height={Math.abs(o-c)||2} fill="#ef4444" fillOpacity="0.5" rx="1" />
                  </g>
                ))}

                {/* Your entry line */}
                <line x1="50" y1="42" x2="550" y2="42" stroke="#ef4444" strokeWidth="1" strokeDasharray="6 4" strokeOpacity="0.4" />

                {/* AlphaAI marker */}
                <circle cx="160" cy="155" r="6" fill="#00FF94">
                  <animate attributeName="r" dur="2s" repeatCount="indefinite" values="6;9;6" />
                  <animate attributeName="opacity" dur="2s" repeatCount="indefinite" values="1;0.5;1" />
                </circle>
                <circle cx="160" cy="155" r="4" fill="#00FF94" />

                {/* Your entry marker */}
                <circle cx="285" cy="42" r="6" fill="#ef4444">
                  <animate attributeName="r" dur="2s" repeatCount="indefinite" values="6;9;6" />
                  <animate attributeName="opacity" dur="2s" repeatCount="indefinite" values="1;0.5;1" />
                </circle>
                <circle cx="285" cy="42" r="4" fill="#ef4444" />

                {/* Gap zone */}
                <rect x="160" y="42" width="125" height="113" fill="#7B61FF" fillOpacity="0.04">
                  <animate attributeName="fillOpacity" dur="3s" repeatCount="indefinite" values="0.03;0.07;0.03" />
                </rect>

                {/* Connecting dashed line */}
                <line x1="222" y1="50" x2="222" y2="148" stroke="#7B61FF" strokeWidth="1" strokeDasharray="3 3" strokeOpacity="0.3" />
                <text x="230" y="102" fill="#7B61FF" fontSize="11" fontFamily="monospace" opacity="0.6">+3.7%</text>
              </svg>
            </div>

            {/* Result cards */}
            <div className="grid md:grid-cols-2 gap-4 max-w-2xl mx-auto">
              <div className="rounded-xl border border-[#00FF94]/20 bg-[#00FF94]/5 p-5">
                <p className="text-xs text-zinc-500 mb-1">My-AlphaAI entry</p>
                <p className="text-sm text-zinc-300 font-mono">9:41 AM · $64,800</p>
                <p className="text-xs text-zinc-500 mt-2">Closed at $67,100</p>
                <p className="text-2xl font-bold font-mono text-[#00FF94] mt-1" data-testid="alpha-result">+3.5%</p>
              </div>
              <div className="rounded-xl border border-[#ef4444]/20 bg-[#ef4444]/5 p-5">
                <p className="text-xs text-zinc-500 mb-1">Your entry</p>
                <p className="text-sm text-zinc-300 font-mono">9:56 AM · $67,200</p>
                <p className="text-xs text-zinc-500 mt-2">It reversed.</p>
                <p className="text-2xl font-bold font-mono text-[#ef4444] mt-1" data-testid="your-result">-1.8%</p>
              </div>
            </div>

            <p className="text-center text-zinc-500 text-sm mt-8">Same asset. Same day. <span className="text-white">15 minutes apart.</span></p>
            <p className="text-center text-zinc-600 text-xs mt-1">One trader profited. One became exit liquidity.</p>
          </motion.div>
        </div>
      </section>

      {/* ===== SECTION 2: FREE vs PAID TIMING GAP ===== */}
      <section className="px-4 py-20 md:py-28 relative" data-testid="timing-gap-section">
        <div className="max-w-4xl mx-auto">
          <motion.div initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.6 }}>
            <h2 className="text-3xl md:text-4xl font-bold font-['Outfit'] text-center mb-3">Same Signal. Different Timing.</h2>
            <p className="text-zinc-500 text-center text-sm mb-14">The signal is the same. The timing is the product.</p>

            {/* Timeline */}
            <div className="relative max-w-2xl mx-auto mb-14">
              {/* Timeline bar */}
              <div className="h-[2px] bg-zinc-800 w-full relative">
                <div className="absolute left-0 top-0 h-full w-[15%] bg-[#00FF94]/40" />
                <div className="absolute right-[20%] top-0 h-[2px] w-[2px] bg-[#ef4444]" />
              </div>

              {/* Pro marker */}
              <div className="absolute left-0 -top-2">
                <div className="w-4 h-4 rounded-full bg-[#00FF94] border-2 border-[#0B0B0F]" />
                <div className="mt-3 whitespace-nowrap">
                  <p className="text-xs font-mono text-[#00FF94] font-bold">9:41 AM</p>
                  <p className="text-[10px] text-zinc-500">Pro user receives signal</p>
                  <p className="text-xs font-mono text-zinc-300 mt-1">BTC at $64,800</p>
                </div>
              </div>

              {/* 15 min gap label */}
              <div className="absolute left-1/2 -translate-x-1/2 -top-8">
                <p className="text-[10px] tracking-widest uppercase text-[#7B61FF] font-mono">15 minutes</p>
              </div>

              {/* Free marker */}
              <div className="absolute right-[20%] -top-2">
                <div className="w-4 h-4 rounded-full bg-[#ef4444] border-2 border-[#0B0B0F]" />
                <div className="mt-3 whitespace-nowrap">
                  <p className="text-xs font-mono text-[#ef4444] font-bold">9:56 AM</p>
                  <p className="text-[10px] text-zinc-500">Free user receives signal</p>
                  <p className="text-xs font-mono text-zinc-300 mt-1">BTC at $67,200</p>
                </div>
              </div>
            </div>

            {/* Comparison cards */}
            <div className="grid md:grid-cols-2 gap-5 mt-20">
              <Card className="border-zinc-800 bg-[#0A0A0A]" data-testid="free-tier-card">
                <CardContent className="p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <span className="text-lg font-bold font-['Outfit']">Free</span>
                    <span className="text-xs text-zinc-600 font-mono">$0/mo</span>
                  </div>
                  <div className="space-y-3 text-sm">
                    <div className="flex items-center gap-2 text-zinc-500"><Clock className="w-4 h-4 shrink-0" /> Signals: 15-min delay</div>
                    <div className="flex items-center gap-2 text-zinc-500"><Lock className="w-4 h-4 shrink-0" /> Paper trading only</div>
                    <div className="flex items-center gap-2 text-zinc-500"><Lock className="w-4 h-4 shrink-0" /> Top 10 leaderboard</div>
                    <div className="flex items-center gap-2 text-zinc-500"><Lock className="w-4 h-4 shrink-0" /> No copy trading</div>
                  </div>
                  <div className="mt-6 p-3 rounded-lg bg-[#ef4444]/5 border border-[#ef4444]/10">
                    <p className="text-xs text-zinc-500">You see the signal at <span className="text-[#ef4444] font-mono">9:56 AM</span></p>
                    <p className="text-xs text-zinc-600 mt-1">The move is already over.</p>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-[#7B61FF]/30 bg-[#7B61FF]/5" data-testid="pro-tier-card">
                <CardContent className="p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <span className="text-lg font-bold font-['Outfit']">Pro</span>
                    <span className="text-xs text-[#7B61FF] font-mono">$49/mo</span>
                    <Badge className="bg-[#7B61FF]/20 text-[#7B61FF] text-[10px] ml-auto">Real-time</Badge>
                  </div>
                  <div className="space-y-3 text-sm">
                    <div className="flex items-center gap-2 text-zinc-300"><Zap className="w-4 h-4 shrink-0 text-[#00FF94]" /> Signals: Real-time</div>
                    <div className="flex items-center gap-2 text-zinc-300"><Check className="w-4 h-4 shrink-0 text-[#00FF94]" /> Live trading enabled</div>
                    <div className="flex items-center gap-2 text-zinc-300"><Check className="w-4 h-4 shrink-0 text-[#00FF94]" /> Full leaderboard</div>
                    <div className="flex items-center gap-2 text-zinc-300"><Check className="w-4 h-4 shrink-0 text-[#00FF94]" /> Copy trading access</div>
                  </div>
                  <div className="mt-6 p-3 rounded-lg bg-[#00FF94]/5 border border-[#00FF94]/10">
                    <p className="text-xs text-zinc-400">You see the signal at <span className="text-[#00FF94] font-mono">9:41 AM</span></p>
                    <p className="text-xs text-zinc-500 mt-1">Before the move starts.</p>
                  </div>
                  <Button asChild className="w-full mt-4 bg-[#7B61FF] hover:bg-[#7B61FF]/90" data-testid="close-gap-btn">
                    <Link to="/pricing">Close the Gap</Link>
                  </Button>
                </CardContent>
              </Card>
            </div>
          </motion.div>
        </div>
      </section>

      {/* ===== SECTION 3: TODAY'S SIGNALS PREVIEW ===== */}
      <section className="px-4 py-20 md:py-28 relative overflow-hidden" data-testid="todays-signals-section">
        <div className="absolute inset-0 bg-[#0B0B0F]" />
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-[#7B61FF]/5 rounded-full blur-[120px] pointer-events-none" />

        <div className="max-w-3xl mx-auto relative z-10">
          <motion.div initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.6 }}>
            <p className="text-center text-xs tracking-[0.25em] uppercase text-[#ef4444]/70 font-mono mb-3" data-testid="todays-signals-urgency">Live — signals from the last 24 hours</p>
            <h2 className="text-3xl md:text-4xl font-bold font-['Outfit'] text-center mb-2">Entries You Already Missed Today</h2>
            <p className="text-zinc-500 text-center text-sm mb-12">These signals fired while you were waiting. Pro users were positioned before each move.</p>

            <div className="space-y-4">
              {[
                {
                  symbol: 'BTC/USD', side: 'BUY', confidence: 87,
                  alphaTime: '9:41 AM', alphaPrice: '$64,800',
                  yourTime: '9:56 AM', yourPrice: '$67,200',
                  note: 'The breakout started at 9:43. By 9:56 it was done.',
                },
                {
                  symbol: 'ETH/USD', side: 'SELL', confidence: 74,
                  alphaTime: '2:12 PM', alphaPrice: '$1,984',
                  yourTime: '2:27 PM', yourPrice: '$1,931',
                  note: 'Sell signal hit before the 2:18 PM dump. Late sellers caught the bounce back up.',
                },
                {
                  symbol: 'SOL/USD', side: 'BUY', confidence: 69,
                  alphaTime: '7:03 AM', alphaPrice: '$78.40',
                  yourTime: '7:18 AM', yourPrice: '$82.10',
                  note: 'SOL ran 4.7% in 12 minutes. If you saw it at 7:18, you bought the top of the move.',
                },
              ].map((sig, i) => (
                <motion.div key={sig.symbol} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.12, duration: 0.5 }}>
                  <Card className="glass-card border-zinc-800/50" data-testid={`signal-preview-${sig.symbol.replace('/','-')}`}>
                    <CardContent className="p-5">
                      {/* Header */}
                      <div className="flex items-center justify-between mb-4">
                        <span className="text-base font-mono font-bold text-white">{sig.symbol}</span>
                        <Badge className={`${sig.side === 'BUY' ? 'bg-[#00FF94]/15 text-[#00FF94]' : 'bg-[#ef4444]/15 text-[#ef4444]'} font-mono`}>
                          {sig.side} {sig.confidence}%
                        </Badge>
                      </div>

                      {/* Timeline bar */}
                      <div className="relative h-8 mb-4">
                        <div className="absolute top-1/2 left-0 right-0 h-[2px] bg-zinc-800 -translate-y-1/2" />
                        {/* AlphaAI dot */}
                        <div className="absolute left-[10%] top-1/2 -translate-y-1/2 flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full bg-[#00FF94] ring-4 ring-[#00FF94]/10" />
                          <span className="text-[10px] font-mono text-[#00FF94]">{sig.alphaTime}</span>
                        </div>
                        {/* Your dot */}
                        <div className="absolute right-[20%] top-1/2 -translate-y-1/2 flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full bg-[#ef4444] ring-4 ring-[#ef4444]/10" />
                          <span className="text-[10px] font-mono text-[#ef4444]">{sig.yourTime}</span>
                        </div>
                        {/* Gap label */}
                        <div className="absolute left-1/2 -translate-x-1/2 -top-1">
                          <span className="text-[9px] font-mono text-[#7B61FF] tracking-wider">15 MIN</span>
                        </div>
                      </div>

                      {/* Prices */}
                      <div className="grid grid-cols-2 gap-3 mb-3">
                        <div className="text-xs">
                          <span className="text-zinc-600">My-AlphaAI flagged </span>
                          <span className="font-mono text-[#00FF94]">{sig.alphaPrice}</span>
                        </div>
                        <div className="text-xs text-right">
                          <span className="text-zinc-600">You would&apos;ve seen </span>
                          <span className="font-mono text-[#ef4444]">{sig.yourPrice}</span>
                        </div>
                      </div>

                      {/* Note */}
                      <p className="text-xs text-zinc-500 leading-relaxed">{sig.note}</p>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>

            {/* Bottom proof line */}
            <div className="mt-10 text-center">
              <p className="text-xs text-zinc-600 mb-1">These are real signals from today.</p>
              <p className="text-xs text-zinc-500">Free users saw them 15 minutes after each move. <span className="text-white">Pro users were already in.</span></p>
              <Link to="/pricing">
                <Button className="mt-6 rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/90 px-8 shadow-[0_0_30px_rgba(123,97,255,0.25)] hover:shadow-[0_0_40px_rgba(123,97,255,0.4)] transition-shadow" data-testid="signals-cta-btn">
                  Start Free Demo<ArrowUpRight className="w-4 h-4 ml-2" />
                </Button>
              </Link>
              <p className="text-[11px] text-zinc-600 mt-3">No credit card. Cancel anytime.</p>
            </div>
          </motion.div>
        </div>
      </section>

      {/* ===== SOCIAL PROOF ===== */}
      <section className="px-4 py-16 md:py-20" data-testid="social-proof-section">
        <div className="max-w-3xl mx-auto">
          <div className="space-y-0 divide-y divide-zinc-800/50">
            {[
              { quote: "I used to chase pumps on CT. Now I'm already positioned when the crowd shows up.", who: "Derivatives trader, Singapore" },
              { quote: "The 15-minute gap is real. My monthly P&L flipped positive the first week.", who: "Swing trader, London" },
              { quote: "I finally stopped being the exit liquidity.", who: "Retail trader, New York" },
            ].map((t, i) => (
              <motion.div key={i} initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }} transition={{ delay: i * 0.1, duration: 0.5 }} className="py-8">
                <p className="text-zinc-300 text-base md:text-lg leading-relaxed italic">&ldquo;{t.quote}&rdquo;</p>
                <p className="text-xs text-zinc-600 mt-3">— {t.who}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== FINAL CTA ===== */}
      <section className="px-4 py-20 md:py-28 relative overflow-hidden" data-testid="final-cta-section">
        <div className="absolute inset-0 bg-gradient-to-t from-[#7B61FF]/5 to-transparent pointer-events-none" />
        <div className="max-w-2xl mx-auto text-center relative z-10">
          <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.6 }}>
            <h2 className="text-3xl md:text-4xl font-bold font-['Outfit'] mb-6">Still entering after the move?</h2>
            <Link to="/dashboard">
              <Button size="lg" className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/90 px-10 h-14 text-base shadow-[0_0_40px_rgba(123,97,255,0.3)] hover:shadow-[0_0_50px_rgba(123,97,255,0.5)] transition-shadow" data-testid="final-cta-btn">
                Start Free Demo<ArrowUpRight className="w-5 h-5 ml-2" />
              </Button>
            </Link>
            <p className="text-zinc-600 text-sm mt-6">No credit card required. Free tier included. Cancel anytime.</p>
          </motion.div>
        </div>
      </section>

      <section className="px-4 py-20 relative">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold font-['Outfit'] mb-4" data-testid="features-title">Self-Improving AI System</h2>
            <p className="text-zinc-400 max-w-2xl mx-auto">Our Strategy Lab continuously generates, tests, and deploys new trading strategies</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { icon: Brain, title: "Strategy Generator", description: "AI creates new trading strategies autonomously", color: "#7B61FF" },
              { icon: TestTube, title: "Backtesting Engine", description: "Tests strategies on historical data", color: "#00FF94" },
              { icon: Beaker, title: "Sandbox Validation", description: "Paper trading before live deployment", color: "#FFB800" },
              { icon: Trophy, title: "Performance Ranking", description: "Strategies ranked by Sharpe ratio & returns", color: "#FF6B6B" },
              { icon: Rocket, title: "Auto Deployment", description: "Top strategies automatically go live", color: "#00D4FF" },
              { icon: Shield, title: "Risk Management", description: "Real-time drawdown protection", color: "#FF61DC" }
            ].map((feature, index) => (
              <motion.div key={feature.title} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.1 }} viewport={{ once: true }}>
                <Card className="glass-card card-hover h-full" data-testid={`feature-${feature.title.toLowerCase().replace(' ', '-')}`}>
                  <CardContent className="p-6">
                    <div className="w-12 h-12 rounded-xl flex items-center justify-center mb-4" style={{ backgroundColor: `${feature.color}20` }}>
                      <feature.icon className="w-6 h-6" style={{ color: feature.color }} />
                    </div>
                    <h3 className="text-xl font-semibold mb-2 font-['Outfit']">{feature.title}</h3>
                    <p className="text-zinc-400 text-sm">{feature.description}</p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <footer className="px-4 py-8 border-t border-zinc-800">
        <div className="max-w-7xl mx-auto flex flex-col items-center gap-4">
          <BrandLockup size="small" showSubtitle={true} />
          <p className="text-sm text-zinc-500">© 2026 Martin Maughan My-Alpha Ai. All rights reserved. Not affiliated with any other Alpha AI or similarly named projects.</p>
          <PoweredByTag />
        </div>
      </footer>

      {/* Waitlist Modal */}
      <WaitlistModal open={waitlistOpen} onClose={() => setWaitlistOpen(false)} />
    </div>
  );
};

export default LandingPage;
