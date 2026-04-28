import { useEffect, useRef } from "react";
import { getWallet } from "@/lib/api";

// ---------------------------------------------------------------------------
// useReferralPing
// ---------------------------------------------------------------------------
// Lightweight wallet poller that fires a toast every time the inviter's
// `referral_credits` ticks up (i.e. someone they invited took an action).
//
// Design notes:
//   • Skips polling while the document is hidden (visibilitychange listener)
//     so backgrounded tabs don't burn battery / Railway egress.
//   • Triggers an immediate re-check the moment the tab regains focus, so a
//     friend joining while you were on Instagram still gets dopamine.
//   • The very first fetch establishes the baseline silently — only deltas
//     produce a toast.
//   • Best-effort: any error is swallowed.
//   • Returns nothing — purely a side-effect hook.
// ---------------------------------------------------------------------------

export function useReferralPing(userId, toast, intervalMs = 30000) {
  // Last-seen referral_credits. `null` means "we haven't fetched yet" — used
  // to suppress the toast on the very first poll.
  const lastSeenRef = useRef(null);
  const timerRef = useRef(null);
  const inflightRef = useRef(false);

  useEffect(() => {
    if (!userId || !toast) return undefined;

    let cancelled = false;

    const ping = async () => {
      if (cancelled || inflightRef.current) return;
      if (typeof document !== "undefined" && document.visibilityState === "hidden") {
        return; // skip while backgrounded
      }
      inflightRef.current = true;
      try {
        const w = await getWallet(userId);
        if (cancelled) return;
        const next = Number(w?.referral_credits ?? 0);
        const prev = lastSeenRef.current;

        // First fetch establishes the baseline silently.
        if (prev == null) {
          lastSeenRef.current = next;
          return;
        }

        if (next > prev) {
          const delta = next - prev;
          const friendCount = Math.max(1, Math.round(delta / 5));
          const noun = friendCount === 1 ? "friend" : "friends";
          // Fire the dopamine toast.
          toast.success(
            `🎉 +${delta} Vibe Credits! ${friendCount} ${noun} joined via your link.`
          );
        }

        lastSeenRef.current = next;
      } catch {
        // network blip or 4xx — we'll just retry on the next tick
      } finally {
        inflightRef.current = false;
      }
    };

    // Fire once on mount (after a short delay so it doesn't race the
    // initial Home fetch). Then poll every `intervalMs`.
    const startTimer = () => {
      if (timerRef.current) return;
      timerRef.current = window.setInterval(ping, intervalMs);
    };
    const stopTimer = () => {
      if (timerRef.current) {
        window.clearInterval(timerRef.current);
        timerRef.current = null;
      }
    };

    const onVisibility = () => {
      if (document.visibilityState === "visible") {
        // Returning to the tab — poll right away then resume normal cadence.
        ping();
        startTimer();
      } else {
        stopTimer();
      }
    };

    // Initial baseline fetch (silent — no toast on first pull).
    const bootstrap = window.setTimeout(ping, 1500);
    startTimer();
    if (typeof document !== "undefined") {
      document.addEventListener("visibilitychange", onVisibility);
    }

    return () => {
      cancelled = true;
      window.clearTimeout(bootstrap);
      stopTimer();
      if (typeof document !== "undefined") {
        document.removeEventListener("visibilitychange", onVisibility);
      }
    };
  }, [userId, toast, intervalMs]);
}
