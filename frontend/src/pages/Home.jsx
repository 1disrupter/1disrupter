import React, {
  useState,
  useEffect,
  useCallback,
  useMemo,
} from "react";

import {
  Navbar,
  MapPinIcon,
  VenueHeroCard,
  VenueCardSkeleton,
  EmptyState,
  ErrorState,
  useToast,
} from "@/components/v2n";

import { getTopVibes } from "@/lib/api";

export default function Home() {
  const toast = useToast();

  const [loc, setLoc] = useState({
    lat: 36.595,
    lng: -4.571,
    label: "Benalmádena",
  });

  const [radius] = useState(5);
  const [vibes, setVibes] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch vibes
  const fetchVibes = useCallback(async (l = loc, r = radius) => {
  try {
    setLoading(true);
    const data = await getTopVibes(l.lat, l.lng, r);
    setVibes(data);
    setError(null);
  } catch (err) {
    setError(err.message);
  } finally {
    setLoading(false);
  }
}, [loc, radius]); // stable, no deps

  // Initial load
  useEffect(() => {
    fetchVibes(loc, radius);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Use my location
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const useMyLocation = useCallback(() => {
    if (!navigator.geolocation) {
      toast.warn("Geolocation not available on this device.");
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const next = {
          lat: pos.coords.latitude,
          lng: pos.coords.longitude,
          label: "Your Location",
        };
        setLoc(next);
        toast.success("Location updated.");
        fetchVibes(next, radius);
      },
      () => toast.warn("Please enable location to see venues near you."),
      { enableHighAccuracy: true, timeout: 8000 }
    );
  }, [toast, radius, fetchVibes]);

  // Slots
  const slots = useMemo(
    () => [
      { key: "best_overall", data: vibes?.best_overall },
      { key: "live_music", data: vibes?.live_music },
      { key: "hidden_gem", data: vibes?.hidden_gem },
    ],
    [vibes]
  );

  return (
    <div className="min-h-screen bg-black text-white">
      <Navbar />

      <div className="p-4 space-y-6">
        {/* Location Header */}
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            <MapPinIcon size={18} />
            {loc.label}
          </h2>

          <button
            onClick={useMyLocation}
            className="text-sm text-white/70 hover:text-white"
          >
            Use my location
          </button>
        </div>

        {/* Error */}
        {error && <ErrorState message={error} />}

        {/* Loading */}
        {loading && (
          <div className="grid gap-4 md:grid-cols-3">
            <VenueCardSkeleton />
            <VenueCardSkeleton />
            <VenueCardSkeleton />
          </div>
        )}

        {/* Content */}
        {!loading && !error && (
          <div className="space-y-6">
            {slots.map((s) =>
              s.data ? (
                <VenueHeroCard
                  key={s.key}
                  slot={s.key}
                  data={s.data}
                  onGo={() => {}}
                />
              ) : null
            )}

            {!vibes?.best_overall &&
              !vibes?.live_music &&
              !vibes?.hidden_gem && <EmptyState />}
          </div>
        )}
      </div>
    </div>
  );






