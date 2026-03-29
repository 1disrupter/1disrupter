/**
 * AlphaAI Analytics Abstraction
 *
 * Swap the implementation inside `track()` to wire up
 * PostHog, Mixpanel, Amplitude, or a custom backend.
 */
import { API } from './constants';

const QUEUE_KEY = 'alphaai_analytics_queue';

const flush = async (events) => {
  try {
    await fetch(`${API}/analytics/events`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ events }),
      keepalive: true,
    });
  } catch {
    // Network failure — re-queue for next flush
    const prev = JSON.parse(sessionStorage.getItem(QUEUE_KEY) || '[]');
    sessionStorage.setItem(QUEUE_KEY, JSON.stringify([...prev, ...events]));
  }
};

const analytics = {
  /**
   * Track an event.  Non-blocking — fires and forgets.
   * @param {string} eventName
   * @param {Record<string, any>} payload
   */
  track(eventName, payload = {}) {
    const event = {
      event: eventName,
      timestamp: new Date().toISOString(),
      ...payload,
    };

    // Log locally for dev visibility
    if (process.env.NODE_ENV === 'development') {
      console.log('[analytics]', eventName, payload);
    }

    // Flush queued events + current event in one call
    const queued = JSON.parse(sessionStorage.getItem(QUEUE_KEY) || '[]');
    sessionStorage.removeItem(QUEUE_KEY);
    flush([...queued, event]);
  },
};

export default analytics;
