import axios from "axios";
import { API } from "./constants";

/**
 * Track a user event. Fire-and-forget — never blocks UI.
 * @param {string} type - Event type (page_view, api_call, strategy_view, follow, unfollow, signal, ws_connect, ws_disconnect, upgrade_prompt, checkout_start, checkout_success, error)
 * @param {object} metadata - Extra data (path, asset, error message, etc.)
 */
export const trackEvent = (type, metadata = {}) => {
  try {
    // Tag demo mode
    const isDemo = sessionStorage.getItem("alphaai_demo_mode") === "true";
    const payload = {
      type,
      metadata: { ...metadata, demo: isDemo },
    };

    // Get token if available
    const stored = localStorage.getItem("alphaai_tokens");
    const headers = {};
    if (stored) {
      try {
        const tokens = JSON.parse(stored);
        if (tokens?.access_token) {
          headers.Authorization = `Bearer ${tokens.access_token}`;
        }
      } catch {
        // no-op
      }
    }

    // Fire and forget — don't await
    axios.post(`${API}/admin/events`, payload, { headers }).catch(() => {});
  } catch {
    // Never let tracking break the app
  }
};

/**
 * Track a page view event with the current path.
 * @param {string} path - URL path
 */
export const trackPageView = (path) => {
  trackEvent("page_view", { path, referrer: document.referrer || "(direct)" });
};

/**
 * Track an API call with latency.
 * @param {string} endpoint - API endpoint called
 * @param {number} latencyMs - Round-trip time in ms
 * @param {number} status - HTTP status code
 */
export const trackApiCall = (endpoint, latencyMs, status) => {
  trackEvent("api_call", { endpoint, latency_ms: latencyMs, status });
};

/**
 * Track a frontend error.
 * @param {string} message - Error message
 * @param {string} source - Component or file source
 */
export const trackError = (message, source = "unknown") => {
  trackEvent("error", { message, source });
};
