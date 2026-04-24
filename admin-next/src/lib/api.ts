// Typed fetch client for the Vibe2Nite backend.
export const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ||
  (typeof window !== "undefined" ? window.location.origin : "http://localhost:8001");

export type Category = "bar" | "club" | "live_music";
export type Crowd = "busy" | "medium" | "dead";
export type Trend = "rising" | "peaking" | "falling" | "steady";
export type TouristLabel = "tourist_trap" | "local_gem" | "neutral";

export interface VenueOut {
  id: string;
  name: string;
  category: Category;
  latitude: number;
  longitude: number;
}
export interface SignalsOut {
  manual_score: number;
  social_activity: number;
  user_votes: number;
  time_prediction: number;
  venue_boost: number;
}
export interface VibeOut {
  venue_id: string;
  vibe_score: number;
  crowd_level: Crowd;
  last_updated: string;
  signals: SignalsOut;
}
export interface ExternalSignals {
  google_score: number;
  social_score: number;
  event_score: number;
  time_score: number;
  user_votes_score: number;
  updated_at: string;
}
export interface AdminVenueRow {
  venue: VenueOut;
  vibe: VibeOut;
  external_signals: ExternalSignals | null;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}/api${path}`, {
    headers: { "Content-Type": "application/json" },
    cache: "no-store",
    ...init,
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText} — ${body || path}`);
  }
  return (await res.json()) as T;
}

export const listAdminVenues = () =>
  request<{ count: number; items: AdminVenueRow[] }>(`/admin/venues`);

export const createVenue = (body: {
  name: string; category: Category; latitude: number; longitude: number;
}) => request<VenueOut>(`/admin/venues`, { method: "POST", body: JSON.stringify(body) });

export const updateSignals = (
  venue_id: string,
  body: Partial<Pick<SignalsOut, "manual_score" | "social_activity" | "time_prediction" | "venue_boost">>
) => request<VibeOut>(`/admin/venues/${venue_id}/signals`, { method: "PATCH", body: JSON.stringify(body) });

export const triggerSignalRefresh = () =>
  request<{ status: string; refreshed: number; errors: number; total: number }>(
    `/admin/signals/refresh`,
    { method: "POST" }
  );

export const getTouristFlags = () =>
  request<{ count: number; buckets: Record<TouristLabel, number>; items: any[] }>(
    `/vibes/tourist-flags`
  );

export const getForecast = () =>
  request<{ count: number; items: { venue_id: string; name: string; trend: Trend; delta_next_hour: number; current_vibe_score: number; as_of: string }[] }>(
    `/vibes/forecast`
  );

export const getLiveMusic = () =>
  request<{ count: number; items: any[] }>(`/vibes/live-music?include_all=true`);

export const getHeatmap = () =>
  request<{ count: number; points: { id: string; name: string; category: Category; lat: number; lng: number; heat: number }[] }>(`/vibes/heatmap`);

// ---------------------------------------------------------------------------
// Rewards — Vibe Credits economy
// ---------------------------------------------------------------------------
export interface RewardOffer {
  id: string;
  venue_id: string;
  name: string;
  description: string;
  cost_credits: number;
  active: boolean;
  created_at: string;
}
export interface Redemption {
  id: string;
  user_id: string;
  venue_id: string;
  offer_id: string;
  cost_credits: number;
  timestamp: string;
}

export const getRewardRules = () => request<Record<string, number>>(`/rewards/rules`);

export const listOffers = (venue_id?: string, active_only = false) =>
  request<RewardOffer[]>(
    `/rewards/offers${venue_id ? `?venue_id=${venue_id}&active_only=${active_only}` : `?active_only=${active_only}`}`
  );

export const createRewardOffer = (body: {
  venue_id: string; name: string; cost_credits: number; description?: string; active?: boolean;
}) => request<RewardOffer>(`/rewards/offers`, { method: "POST", body: JSON.stringify(body) });

export const deactivateRewardOffer = (id: string) =>
  request<RewardOffer>(`/rewards/offers/${id}`, { method: "DELETE" });

export const lookupWallet = (user_id: string) =>
  request<{ user_id: string; credits: number; updated_at: string }>(
    `/rewards/wallet/${encodeURIComponent(user_id)}?create=false`
  );

export const grantCredits = (user_id: string, amount: number) =>
  request<{ user_id: string; action: string; awarded: number; credits: number }>(
    `/rewards/earn`,
    { method: "POST", body: JSON.stringify({ user_id, action: "admin_grant", amount }) }
  );

export const listRedemptions = (params?: { venue_id?: string; user_id?: string; limit?: number }) => {
  const qs = new URLSearchParams();
  if (params?.venue_id) qs.set("venue_id", params.venue_id);
  if (params?.user_id) qs.set("user_id", params.user_id);
  if (params?.limit) qs.set("limit", String(params.limit));
  const s = qs.toString();
  return request<Redemption[]>(`/rewards/redemptions${s ? `?${s}` : ""}`);
};

// ---------------------------------------------------------------------------
// Intel — trajectory / flow
// ---------------------------------------------------------------------------
export interface TrajectoryPoint { timestamp: string; vibe_score: number }
export interface FlowRow {
  venue_id: string; name: string; flow: Trend; pings_now: number; pings_past: number;
}

export const getTrajectory = (venue_id: string, hours = 6) =>
  request<TrajectoryPoint[]>(`/intel/trajectory/${venue_id}?hours=${hours}`);

export const getFlow = () => request<FlowRow[]>(`/intel/flow`);

// P3 — forecast, intel-v2, local gems, launch, push inbox, push triggers
export type ForecastTrend = "rising" | "falling" | "steady" | "peaking";
export interface VenueForecast {
  venue_id: string;
  current_score: number;
  forecast_score: number;
  trend: ForecastTrend;
  confidence: number;
  momentum: number;
  baseline: number;
  cycle_boost: number;
  horizon_hours: number;
  as_of: string;
  cached: boolean;
}
export const getVenueForecast = (venue_id: string) =>
  request<VenueForecast>(`/forecast/${venue_id}`);

export type TouristLabelV2 = "tourist_trap" | "local_gem" | "neutral";
export interface IntelFlag { venue_id: string; label: TouristLabelV2; score: number; reason: string; updated_at: string }
export const getIntelTouristFlags = () => request<{ items: IntelFlag[] }>(`/intel/tourist-flags`);
export const refreshIntelTouristFlags = () =>
  request<{ items: IntelFlag[] }>(`/intel/tourist-flags/refresh`, { method: "POST" });

export interface LocalGem {
  venue_id: string; name: string; category: Category; lat: number; lng: number;
  vibe_score: number; gem_score: number; label: TouristLabelV2; rank: number;
}
export const getLocalGems = (limit = 10) =>
  request<{ items: LocalGem[] }>(`/intel/local-gems?limit=${limit}`);

export interface PushTriggerIn {
  kind: "daily_login" | "first_visit_bonus" | "vibe_spike" | "offer_drop" | "tonight_hotspots";
  wallet_id?: string;
  venue_id?: string;
  offer_name?: string;
  cost?: number;
  offer_id?: string;
  score?: number;
  top_names?: string[];
}
export const triggerPush = (body: PushTriggerIn) =>
  request<{ kind: string; sent_to?: number; dispatched?: number }>(
    `/notifications/trigger/test`,
    { method: "POST", body: JSON.stringify(body) }
  );

export interface CitySeedVenue {
  name: string; category: "bar" | "club" | "live_music"; latitude: number; longitude: number;
  opening_hours?: Record<string, string>; music_type?: string; price_level?: number;
  age_group?: string; dress_code?: string; photos?: string[];
}
export const seedCity = (city: string, venues: CitySeedVenue[]) =>
  request<{ city: string; created: number; updated: number; total: number }>(
    `/city/seed`, { method: "POST", body: JSON.stringify({ city, venues }) }
  );

export const onboardVenue = (body: {
  venue_id: string; username: string; password: string; public_base_url?: string;
}) => request<{
  venue_id: string; username: string; api_key: string;
  qr_codes: { check_in: string; feedback: string; follow_venue: string };
}>(`/venues/onboard`, { method: "POST", body: JSON.stringify(body) });

// P2 — travel time enrichment
export interface IntelScore {
  id: string;
  name: string;
  category: Category;
  lat: number;
  lng: number;
  vibe_score: number;
  crowd_level: Crowd | null;
  external_signals: ExternalSignals | null;
  distance_km?: number;
  walking_time_minutes?: number;
  driving_time_minutes?: number;
  travel_provider?: "stub" | "google";
}
export const getIntelScore = (venue_id: string, user_lat?: number, user_lng?: number) => {
  const qs = new URLSearchParams();
  if (user_lat !== undefined) qs.set("user_lat", String(user_lat));
  if (user_lng !== undefined) qs.set("user_lng", String(user_lng));
  const s = qs.toString();
  return request<IntelScore>(`/intel/score/${venue_id}${s ? `?${s}` : ""}`);
};
