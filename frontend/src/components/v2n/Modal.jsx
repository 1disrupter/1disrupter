import React, { useEffect } from "react";
import { createPortal } from "react-dom";
import { motion, AnimatePresence } from "framer-motion";
import { X } from "lucide-react";
import { cx } from "@/lib/cx";

export function Modal({ open, onClose, title, children, size = "md", footer, className }) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e) => e.key === "Escape" && onClose?.();
    window.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [open, onClose]);

  const widths = { sm: "max-w-sm", md: "max-w-lg", lg: "max-w-2xl", xl: "max-w-4xl" };

  return createPortal(
    <AnimatePresence>
      {open && (
        <motion.div
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          data-testid="modal-overlay"
        >
          <div
            className="absolute inset-0 bg-[#05050A]/80 backdrop-blur-md"
            onClick={onClose}
          />
          <motion.div
            role="dialog"
            aria-modal="true"
            initial={{ opacity: 0, y: 20, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.97 }}
            transition={{ duration: 0.25, ease: [0.2, 0.8, 0.2, 1] }}
            className={cx(
              "relative w-full rounded-xl3 border border-primary-glow/30 bg-background-dark",
              "shadow-[0_30px_80px_-30px_rgba(138,43,226,0.7)]",
              widths[size],
              className
            )}
          >
            <div className="flex items-center justify-between border-b border-white/10 px-5 py-4">
              <h3 className="font-display text-2xl tracking-wider text-white">{title}</h3>
              <button
                onClick={onClose}
                className="rounded-full p-2 text-white/60 hover:text-white hover:bg-white/10"
                data-testid="modal-close"
                aria-label="Close"
              >
                <X size={18} />
              </button>
            </div>
            <div className="max-h-[70vh] overflow-y-auto p-5">{children}</div>
            {footer && (
              <div className="flex items-center justify-end gap-3 border-t border-white/10 px-5 py-4">
                {footer}
              </div>
            )}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>,
    document.body
  );
}
