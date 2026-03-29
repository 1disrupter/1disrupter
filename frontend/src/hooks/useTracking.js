import { useEffect, useRef } from "react";
import { useLocation } from "react-router-dom";
import { trackPageView, trackError } from "../lib/tracking";

/**
 * Global tracking hook. Mount once in App.js.
 * - Fires page_view on every route change.
 * - Catches unhandled errors and tracks them.
 */
const useTracking = () => {
  const location = useLocation();
  const prevPath = useRef(null);

  // Track page views on route change
  useEffect(() => {
    if (location.pathname !== prevPath.current) {
      prevPath.current = location.pathname;
      trackPageView(location.pathname);
    }
  }, [location.pathname]);

  // Global error handler
  useEffect(() => {
    const handler = (event) => {
      trackError(event.message || "Unhandled error", event.filename || "global");
    };
    const rejectionHandler = (event) => {
      trackError(String(event.reason), "unhandled_promise");
    };
    window.addEventListener("error", handler);
    window.addEventListener("unhandledrejection", rejectionHandler);
    return () => {
      window.removeEventListener("error", handler);
      window.removeEventListener("unhandledrejection", rejectionHandler);
    };
  }, []);
};

export default useTracking;
