import axios from "axios";
import { API } from "./constants";

/**
 * Automatic Frontend Tracking Middleware
 * Intercepts axios requests to measure latency and track API calls.
 * Listens to route changes for page view tracking.
 * Sends data to POST /api/admin/track when demo mode is OFF.
 */

let _initialized = false;

/**
 * Fire-and-forget tracker that posts to /api/admin/track.
 * Uses navigator.sendBeacon when available for reliability on page unload.
 */
const sendTrackEvent = (eventType, metadata = {}) => {
  const payload = {
    event_type: eventType,
    metadata,
  };
  try {
    const blob = new Blob([JSON.stringify(payload)], { type: "application/json" });
    if (navigator.sendBeacon) {
      navigator.sendBeacon(`${API}/admin/track`, blob);
    } else {
      fetch(`${API}/admin/track`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
        keepalive: true,
      }).catch(() => {});
    }
  } catch {
    // Never block the app
  }
};

/**
 * Install axios request/response interceptors to auto-track API calls.
 * Measures round-trip latency and records endpoint + status.
 */
const installAxiosInterceptor = () => {
  // Mark request start time
  axios.interceptors.request.use(
    (config) => {
      config._trackStart = performance.now();
      return config;
    },
    (error) => Promise.reject(error)
  );

  // Track response
  axios.interceptors.response.use(
    (response) => {
      const latency = response.config._trackStart
        ? Math.round(performance.now() - response.config._trackStart)
        : 0;
      const url = response.config.url || "";
      // Skip tracking the track endpoint itself to avoid infinite loop
      if (!url.includes("/admin/track") && !url.includes("/admin/events")) {
        const endpoint = url.replace(API, "").split("?")[0];
        sendTrackEvent("api_call", {
          endpoint,
          method: (response.config.method || "get").toUpperCase(),
          status: response.status,
          latency_ms: latency,
        });
      }
      return response;
    },
    (error) => {
      if (error.config) {
        const latency = error.config._trackStart
          ? Math.round(performance.now() - error.config._trackStart)
          : 0;
        const url = error.config.url || "";
        if (!url.includes("/admin/track") && !url.includes("/admin/events")) {
          const endpoint = url.replace(API, "").split("?")[0];
          sendTrackEvent("api_call", {
            endpoint,
            method: (error.config.method || "get").toUpperCase(),
            status: error.response?.status || 0,
            latency_ms: latency,
            error: true,
          });
        }
      }
      return Promise.reject(error);
    }
  );
};

/**
 * Track a page view event via the /api/admin/track endpoint.
 */
export const trackPageViewEvent = (path) => {
  sendTrackEvent("page_view", {
    path,
    referrer: document.referrer || "(direct)",
    user_agent: navigator.userAgent,
  });
};

/**
 * Initialize the tracking middleware. Safe to call multiple times — only runs once.
 */
export const initTrackingMiddleware = () => {
  if (_initialized) return;
  _initialized = true;
  installAxiosInterceptor();
};
