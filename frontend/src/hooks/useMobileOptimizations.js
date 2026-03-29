/**
 * useMobileOptimizations — Handles visibility changes, network status,
 * auto-refresh, and offline queue flushing.
 */
import { useState, useEffect, useCallback, useRef } from "react";
import { flushOfflineQueue } from "../lib/mobileApi";
import { cacheInvalidateOnAuth } from "../lib/mobileCache";

const useMobileOptimizations = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [isVisible, setIsVisible] = useState(!document.hidden);
  const wasOffline = useRef(false);

  // ── Network status ───────────────────────────────────────────

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      // Flush queued events when coming back online
      if (wasOffline.current) {
        wasOffline.current = false;
        flushOfflineQueue();
      }
    };
    const handleOffline = () => {
      setIsOnline(false);
      wasOffline.current = true;
    };

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);
    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  // ── Visibility change (app backgrounding/resuming) ───────────

  useEffect(() => {
    const handler = () => {
      const visible = !document.hidden;
      setIsVisible(visible);
      if (visible) {
        // Flush offline queue on resume
        flushOfflineQueue();
      }
    };
    document.addEventListener("visibilitychange", handler);
    return () => document.removeEventListener("visibilitychange", handler);
  }, []);

  // ── Cache invalidation on auth events ────────────────────────

  const invalidateOnAuth = useCallback(() => {
    cacheInvalidateOnAuth();
  }, []);

  return { isOnline, isVisible, invalidateOnAuth };
};

export default useMobileOptimizations;
