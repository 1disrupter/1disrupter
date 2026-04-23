import { API_BASE } from "@/config";

export type Category = "bar" | "club" | "live_music";
export type VibeFilter = Category | "all";
export type Trend = "rising" | "peaking" | "falling" | "steady";
export type TouristLabel = "tourist_trap" | "local_gem" | "neutral";
export type VoteType = "busy" | "dead" | "good";

export interface Top3Item {
  id: string;
  name: string;
  category: Category;
  vibe_score: number;
  adjusted_score: number;
  lat: number;
  lng: number;
  distance_km: number | null;
  tourist_label: TouristLabel;
}

export interface HeatPoint {
  id: string;
  name: string;
  category: Category;
  lat: number;
  lng: number;
  heat: number;
}

export interface LiveMusicItem {
  venue_id: string;
  name: string;
  category: Category;
  lat: number;
  lng: number;
  live_music: boolean;
  confidence: number;
  event_score: number;
  vibe_score: number;
  reason: string;
}

export interface TouristFlagItem {
  venue_id: string;
  name: string;
  category: Category;
  label: TouristLabel;
  reason: string;
  signals: { google_score: number; social_score: number; user_votes_score: number };
}

export interface ForecastItem {
  venue_id: string;
  name: string;
  trend: Trend;
  delta_next_hour: number;
  current_vibe_score: number;
  as_of: string;
}

export interface Directions {
  venue_id: string;
  duration_minutes: number;
  distance_meters: number;
  deeplink: string;
  provider: "stub" | "google";
}

// ---------------------------------------------------------------------------
// fetch wrapper (no axios — keep RN bundle small)
// ---------------------------------------------------------------------------
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText} — ${body || path}`);
  }
  return (await res.json()) as T;
}

const qs = (p: Record<string, unknown>) => {
  const s = new URLSearchParams();
  for (const [k, v] of Object.entries(p)) {
    if (v === undefined || v === null || v === "") continue;
    s.append(k, String(v));
  }
  const str = s.toString();
  return str ? `?${str}` : "";
};

// ---------------------------------------------------------------------------
// Endpoints
// ---------------------------------------------------------------------------
export const getTop3 = (params: {
  user_lat?: number;
  user_lng?: number;
  vibe?: Category;
  avoid_tourist_traps?: boolean;
  radius_km?: number;
}) => request<{ count: number; items: Top3Item[] }>(`/vibes/top3${qs(params)}`);

export const getHeatmap = () =>
  request<{ count: number; points: HeatPoint[] }>(`/vibes/heatmap`);

export const getLiveMusic = (include_all = false) =>
  request<{ count: number; items: LiveMusicItem[] }>(
    `/vibes/live-music${qs({ include_all })}`
  );

export const getTouristFlags = () =>
  request<{ count: number; buckets: Record<TouristLabel, number>; items: TouristFlagItem[] }>(
    `/vibes/tourist-flags`
  );

export const getForecastAll = () =>
  request<{ count: number; items: ForecastItem[] }>(`/vibes/forecast`);

export const getDirections = (venue_id: string, user_lat: number, user_lng: number) =>
  request<Directions>(`/vibes/directions${qs({ venue_id, user_lat, user_lng })}`);

export const postFeedback = (venue_id: string, vote: VoteType) =>
  request<{ venue_id: string; new_vibe_score: number; new_crowd_level: string; updated_at: string }>(
    `/feedback`,
    { method: "POST", body: JSON.stringify({ venue_id, vote }) }
  );

// ---------------------------------------------------------------------------
// Rewards
// ---------------------------------------------------------------------------
export interface Wallet { user_id: string; credits: number; updated_at: string }
export interface RewardOffer {
  id: string; venue_id: string; name: string; description: string;
  cost_credits: number; active: boolean; created_at: string;
}
export interface RewardEarn {
  user_id: string; action: string; awarded: number; credits: number;
}
export interface Redemption {
  id: string; user_id: string; venue_id: string; offer_id: string;
  cost_credits: number; timestamp: string;
}

export const getWallet = (user_id: string) =>
  request<Wallet>(`/rewards/wallet/${encodeURIComponent(user_id)}`);

/** Strict wallet lookup — 404 if missing (used by "Restore wallet from code"). */
export const lookupWallet = (user_id: string) =>
  request<Wallet>(`/rewards/wallet/${encodeURIComponent(user_id)}?create=false`);

export const earnCredits = (user_id: string, action: string, amount?: number) =>
  request<RewardEarn>(`/rewards/earn`, {
    method: "POST",
    body: JSON.stringify({ user_id, action, amount }),
  });

export const listVenueOffers = (venue_id: string) =>
  request<RewardOffer[]>(`/rewards/offers?venue_id=${encodeURIComponent(venue_id)}&active_only=true`);

export const listActiveOffers = () =>
  request<RewardOffer[]>(`/rewards/offers?active_only=true`);

export const redeemOffer = (user_id: string, offer_id: string) =>
  request<Redemption>(`/rewards/redeem`, {
    method: "POST",
    body: JSON.stringify({ user_id, offer_id }),
  });

export const listMyRedemptions = (user_id: string, limit = 50) =>
  request<Redemption[]>(`/rewards/redemptions?user_id=${encodeURIComponent(user_id)}&limit=${limit}`);

// ---------------------------------------------------------------------------
// Intel (anonymous ping + trajectory)
// ---------------------------------------------------------------------------
export const postPing = (lat: number, lng: number, device_id?: string) =>
  request<{ id: string; timestamp: string }>(`/intel/ping`, {
    method: "POST",
    body: JSON.stringify({ lat, lng, device_id }),
  });

export interface TrajectoryPoint { timestamp: string; vibe_score: number }
export const getTrajectory = (venue_id: string, hours = 6) =>
  request<TrajectoryPoint[]>(`/intel/trajectory/${venue_id}?hours=${hours}`);

export interface IntelScore {
  id: string;
  name: string;
  category: Category;
  lat: number;
  lng: number;
  vibe_score: number;
  crowd_level: string | null;
  external_signals: Record<string, number> | null;
  distance_km?: number;
  walking_time_minutes?: number;
  driving_time_minutes?: number;
  travel_provider?: "stub" | "google";
}
export const getIntelScore = (venue_id: string, user_lat?: number, user_lng?: number) =>
  request<IntelScore>(
    `/intel/score/${venue_id}${qs({ user_lat, user_lng })}`
  );
