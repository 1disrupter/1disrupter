// ---------------------------------------------------------------------------
// Anonymous identity + referral plumbing
// ---------------------------------------------------------------------------
// Vibe2Nite is "no-account" by design — but the rewards/credits backend keys
// every wallet on a stable opaque user_id string. We persist a single UUID
// per device in localStorage so the same browser always maps to the same
// wallet across sessions.
//
// This module owns three responsibilities:
//   1. getOrCreateUserId()       → my own stable id (referrer when I share)
//   2. capturePendingReferrer()  → on first landing with ?ref=<id>, stash it
//   3. consumePendingReferrer()  → after my first credit-eligible action,
//                                   return + clear the stashed inviter id
//
// Everything is best-effort; failures degrade silently.
// ---------------------------------------------------------------------------

const USER_KEY = "v2n_user_id";
const PENDING_REF_KEY = "v2n_pending_ref";

function safeUUID() {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  // RFC4122 v4-ish fallback for very old browsers.
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

function safeStorage() {
  try {
    if (typeof localStorage !== "undefined") return localStorage;
  } catch {
    // private mode / disabled storage
  }
  return null;
}

export function getOrCreateUserId() {
  const ls = safeStorage();
  if (!ls) return null;
  let id = ls.getItem(USER_KEY);
  if (!id) {
    id = safeUUID();
    try { ls.setItem(USER_KEY, id); } catch { /* quota / disabled */ }
  }
  return id;
}

/**
 * If the current URL carries `?ref=<uuid>`, persist it as the pending
 * referrer (overwriting any previous one) and strip the param from the URL
 * so reloads don't re-trigger anything. No-op if `ref` is missing, malformed,
 * or matches my own user_id (no self-referrals).
 */
export function capturePendingReferrer() {
  if (typeof window === "undefined") return;
  try {
    const params = new URLSearchParams(window.location.search);
    const ref = params.get("ref");
    if (!ref) return;
    if (!/^[0-9a-fA-F-]{16,}$/.test(ref)) return; // basic UUID-ish guard
    const me = getOrCreateUserId();
    if (me && ref === me) {
      // self-referral — silently strip the param and ignore
    } else {
      const ls = safeStorage();
      if (ls) {
        try { ls.setItem(PENDING_REF_KEY, ref); } catch { /* ignore */ }
      }
    }
    params.delete("ref");
    const newQs = params.toString();
    const newUrl = window.location.pathname + (newQs ? `?${newQs}` : "") + window.location.hash;
    window.history.replaceState({}, "", newUrl);
  } catch {
    // ignore — never let referral plumbing break the app
  }
}

/**
 * Atomically read & clear the pending referrer. Returns null if none.
 * Call this after the first credit-eligible action so we credit the
 * inviter exactly once per device.
 */
export function consumePendingReferrer() {
  const ls = safeStorage();
  if (!ls) return null;
  try {
    const ref = ls.getItem(PENDING_REF_KEY);
    if (!ref) return null;
    ls.removeItem(PENDING_REF_KEY);
    return ref;
  } catch {
    return null;
  }
}

export function peekPendingReferrer() {
  const ls = safeStorage();
  if (!ls) return null;
  try { return ls.getItem(PENDING_REF_KEY); } catch { return null; }
}
