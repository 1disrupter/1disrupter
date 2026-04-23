import React, { createContext, useCallback, useContext, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { CheckCircle2, AlertCircle, Info, XCircle, X } from "lucide-react";
import { cx } from "@/lib/cx";

const ToastCtx = createContext(null);
let uid = 0;

const icons = {
  success: <CheckCircle2 className="text-glow-aqua" size={18} />,
  error: <XCircle className="text-accent-pink" size={18} />,
  info: <Info className="text-primary-glow" size={18} />,
  warn: <AlertCircle className="text-status-busy" size={18} />,
};

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  const push = useCallback((toast) => {
    const id = ++uid;
    setToasts((t) => [...t, { id, kind: "info", duration: 3200, ...toast }]);
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), toast.duration || 3200);
  }, []);

  const api = {
    show: push,
    success: (msg, opts = {}) => push({ kind: "success", message: msg, ...opts }),
    error: (msg, opts = {}) => push({ kind: "error", message: msg, ...opts }),
    info: (msg, opts = {}) => push({ kind: "info", message: msg, ...opts }),
    warn: (msg, opts = {}) => push({ kind: "warn", message: msg, ...opts }),
  };

  return (
    <ToastCtx.Provider value={api}>
      {children}
      <div className="pointer-events-none fixed right-4 top-4 z-[60] flex w-80 max-w-[90vw] flex-col gap-2">
        <AnimatePresence>
          {toasts.map((t) => (
            <motion.div
              key={t.id}
              initial={{ opacity: 0, x: 40 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 40 }}
              transition={{ duration: 0.22 }}
              data-testid={`toast-${t.kind}`}
              className={cx(
                "pointer-events-auto flex items-start gap-3 rounded-xl border border-white/10",
                "bg-background-dark/95 p-3 pr-4 shadow-softPurple backdrop-blur-md"
              )}
            >
              <span className="mt-0.5">{icons[t.kind]}</span>
              <div className="flex-1 text-sm text-white/90">
                {t.title && <div className="font-semibold">{t.title}</div>}
                <div className="text-white/80">{t.message}</div>
              </div>
              <button
                onClick={() => setToasts((list) => list.filter((x) => x.id !== t.id))}
                className="rounded p-1 text-white/50 hover:bg-white/10 hover:text-white"
                aria-label="Dismiss"
              >
                <X size={14} />
              </button>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </ToastCtx.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastCtx);
  if (!ctx) throw new Error("useToast must be used within <ToastProvider>");
  return ctx;
}
