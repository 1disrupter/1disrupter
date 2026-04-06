import { motion, AnimatePresence } from "framer-motion";
import { Eye, X } from "lucide-react";
import { useSystemMode } from "../contexts/DemoModeContext";

const DemoModeBanner = () => {
  const { isDemo, setMode } = useSystemMode();

  return (
    <AnimatePresence>
      {isDemo && (
        <motion.div
          initial={{ opacity: 0, y: -32 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -32 }}
          transition={{ type: "spring", stiffness: 400, damping: 30 }}
          className="fixed top-0 left-0 right-0 z-[60] flex items-center justify-center gap-3 py-1.5 px-4 bg-[#7B61FF]/15 border-b border-[#7B61FF]/25 backdrop-blur-md"
          data-testid="demo-mode-global-banner"
        >
          <div className="flex items-center gap-2">
            <div className="w-1.5 h-1.5 rounded-full bg-[#7B61FF] animate-pulse" />
            <Eye className="w-3.5 h-3.5 text-[#7B61FF]" />
            <span className="text-xs font-medium text-[#7B61FF]/90 tracking-wide">
              DEMO MODE — All data is simulated for preview
            </span>
          </div>
          <button
            onClick={() => setMode('live')}
            className="ml-2 p-0.5 rounded hover:bg-white/10 transition-colors"
            data-testid="demo-banner-close"
          >
            <X className="w-3.5 h-3.5 text-[#7B61FF]/60 hover:text-[#7B61FF]" />
          </button>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default DemoModeBanner;
