import { motion, AnimatePresence } from "framer-motion";
import { WifiOff, RefreshCw } from "lucide-react";

const MobileNetworkBanner = ({ isOnline, wsConnected }) => {
  const showOffline = !isOnline;
  const showReconnecting = isOnline && wsConnected === false;

  return (
    <AnimatePresence>
      {showOffline && (
        <motion.div
          key="offline"
          initial={{ y: -40, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: -40, opacity: 0 }}
          className="fixed top-0 left-0 right-0 z-[60] bg-red-500/90 backdrop-blur-sm text-white text-xs py-1.5 px-4 flex items-center justify-center gap-2 safe-area-top"
          data-testid="offline-banner"
        >
          <WifiOff className="w-3.5 h-3.5" />
          You're offline — some features may be unavailable
        </motion.div>
      )}
      {showReconnecting && !showOffline && (
        <motion.div
          key="reconnecting"
          initial={{ y: -40, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: -40, opacity: 0 }}
          className="fixed top-0 left-0 right-0 z-[60] bg-[#FFB800]/90 backdrop-blur-sm text-black text-xs py-1.5 px-4 flex items-center justify-center gap-2 safe-area-top"
          data-testid="reconnecting-banner"
        >
          <RefreshCw className="w-3.5 h-3.5 animate-spin" />
          Reconnecting...
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default MobileNetworkBanner;
