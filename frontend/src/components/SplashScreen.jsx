/**
 * AlphaAI Premium Splash Screen
 * Cinematic 2-second brand reveal with scanline effect.
 * Plays once per session (sessionStorage gated).
 */
import { useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Brain } from 'lucide-react';

const SplashScreen = ({ onComplete }) => {
  const containerRef = useRef(null);

  // Prevent focus trapping — keep body interactive underneath
  useEffect(() => {
    const el = containerRef.current;
    if (el) el.setAttribute('aria-hidden', 'true');
  }, []);

  return (
    <motion.div
      ref={containerRef}
      className="fixed inset-0 z-[200] flex items-center justify-center overflow-hidden"
      style={{ background: '#0B0B0F' }}
      initial={{ opacity: 1 }}
      animate={{ opacity: 0 }}
      transition={{ delay: 2.0, duration: 0.45, ease: [0.4, 0, 0.2, 1] }}
      onAnimationComplete={onComplete}
      data-testid="splash-screen"
    >
      {/* Noise texture overlay */}
      <div
        className="absolute inset-0 opacity-[0.03] pointer-events-none"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")`,
          backgroundSize: '128px 128px',
        }}
      />

      {/* Phase 1 (0.0s–0.4s): Ambient glow fade-in */}
      <motion.div
        className="absolute rounded-full pointer-events-none"
        style={{
          width: 420,
          height: 420,
          background: 'radial-gradient(circle, rgba(123,97,255,0.12) 0%, rgba(123,97,255,0.04) 40%, transparent 70%)',
        }}
        initial={{ scale: 0.3, opacity: 0 }}
        animate={{ scale: [0.3, 1.4, 1.1], opacity: [0, 0.7, 0.5] }}
        transition={{ duration: 1.0, ease: 'easeOut' }}
      />

      {/* Secondary cyan glow */}
      <motion.div
        className="absolute rounded-full pointer-events-none"
        style={{
          width: 280,
          height: 280,
          background: 'radial-gradient(circle, rgba(0,255,148,0.06) 0%, transparent 60%)',
          top: '55%',
          left: '52%',
          transform: 'translate(-50%, -50%)',
        }}
        initial={{ opacity: 0 }}
        animate={{ opacity: [0, 0.4, 0.2] }}
        transition={{ delay: 0.3, duration: 1.2, ease: 'easeOut' }}
      />

      {/* Main lockup container */}
      <div className="relative flex flex-col items-center">

        {/* Logo icon */}
        <motion.div
          className="relative mb-6"
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.1, duration: 0.5, ease: [0.34, 1.56, 0.64, 1] }}
        >
          {/* Glow ring behind icon */}
          <motion.div
            className="absolute inset-0 rounded-2xl"
            style={{ boxShadow: '0 0 40px 8px rgba(123,97,255,0.25)' }}
            initial={{ opacity: 0 }}
            animate={{ opacity: [0, 0.6, 0.3] }}
            transition={{ delay: 0.15, duration: 0.8, ease: 'easeOut' }}
          />
          <div className="w-[72px] h-[72px] rounded-2xl bg-gradient-to-br from-[#7B61FF] to-[#00FF94] flex items-center justify-center relative">
            <Brain className="w-10 h-10 text-white" />
          </div>
        </motion.div>

        {/* Phase 2 (0.4s–1.2s): "AlphaAI" text */}
        <motion.div className="overflow-hidden">
          <motion.h1
            className="text-5xl sm:text-6xl font-bold font-['Outfit'] tracking-tight text-white"
            initial={{ y: 30, opacity: 0, filter: 'blur(12px)' }}
            animate={{ y: 0, opacity: 1, filter: 'blur(0px)' }}
            transition={{ delay: 0.4, duration: 0.6, ease: [0.25, 0.46, 0.45, 0.94] }}
          >
            My-AlphaAI
          </motion.h1>
        </motion.div>

        {/* Phase 3 (1.2s–1.8s): "SIGNAL INTELLIGENCE SYSTEM" with scanline */}
        <div className="relative mt-3">
          <motion.p
            className="text-[11px] sm:text-xs font-light tracking-[0.3em] uppercase text-zinc-400"
            initial={{ opacity: 0, letterSpacing: '0.6em' }}
            animate={{ opacity: 1, letterSpacing: '0.3em' }}
            transition={{ delay: 1.2, duration: 0.55, ease: 'easeOut' }}
          >
            Signal Intelligence System
          </motion.p>

          {/* Scanline sweep */}
          <motion.div
            className="absolute top-0 left-0 h-full w-[2px] pointer-events-none"
            style={{
              background: 'linear-gradient(180deg, transparent, rgba(123,97,255,0.8), transparent)',
              boxShadow: '0 0 8px 2px rgba(123,97,255,0.4)',
            }}
            initial={{ left: '-5%', opacity: 0 }}
            animate={{ left: '105%', opacity: [0, 1, 1, 0] }}
            transition={{ delay: 1.2, duration: 0.6, ease: 'linear' }}
          />
        </div>

        {/* Accent divider line */}
        <motion.div
          className="mt-5 h-[1px]"
          style={{
            background: 'linear-gradient(90deg, transparent, #7B61FF, transparent)',
          }}
          initial={{ width: 0, opacity: 0 }}
          animate={{ width: 180, opacity: 0.6 }}
          transition={{ delay: 1.35, duration: 0.5, ease: 'easeOut' }}
        />

        {/* Phase 4 (1.8s–2.0s): Purple accent pulse */}
        <motion.div
          className="absolute inset-0 rounded-3xl pointer-events-none"
          style={{ boxShadow: '0 0 80px 20px rgba(123,97,255,0.15)' }}
          initial={{ opacity: 0 }}
          animate={{ opacity: [0, 0, 0.5, 0] }}
          transition={{ delay: 1.6, duration: 0.5, ease: 'easeInOut' }}
        />
      </div>
    </motion.div>
  );
};

export default SplashScreen;
