import React, { useEffect, useState, useMemo, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { MapPin, Locate, RefreshCw, ThumbsUp, Flame, Ghost, ShieldCheck, CheckCircle2 } from "lucide-react";
import { motion } from "framer-motion";
import {
  Navbar, Footer, BottomTabs, Logo, LogoMark,
  VenueHeroCard, LoadingScreen, ErrorState, EmptyState,
  Button, IconButton, Chip, SectionDivider, useToast,
  Modal, Input,
} from "@/components/v2n";
import { getTopVibes, submitFeedback, submitClaim, checkInVenue, earnReward } from "@/lib/api";
import { getOrCreateUserId, capturePendingReferrer, consumePendingReferrer } from "@/lib/userId";
import { useReferralPing } from "@/lib/useReferralPing";
import QRScanner from "../components/QRScanner";

const DEFAULT_LOCATION = { lat: 40.73, lng: -73.99, label: "Manhattan, NY" };

// Open the device's native maps app with directions to the venue.
// On mobile this hands off to Apple/Google Maps; on desktop it opens
// Google Maps in a new tab. Pure client-side, no API key required.
function openDirectionsToVenue(data) {
  if (!data?.venue) return;
  const { latitude, longitude } = data.venue;
  const url = `https://www.google.com/maps/dir/?api=1&destination=${latitude},${longitude}&travelmode=walking`;
  window.open(url, "_blank", "noopener,noreferrer");
}
const [showScanner, setShowScanner] = useState(false);

// Compose the share text + URL for a venue. The URL carries:
//   ?v=<venue-id>  ⇒ forward-compatible deep link to highlight the venue
//   ?ref=<my-uuid> ⇒ so the inviter can be credited Vibe Credits when the
//                     recipient takes their first credit-eligible action
function buildShareForVenue(data, myUserId) {
  const { venue, vibe, distance_km } = data;
  const score = vibe.vibe_score.toFixed(1);
  const flame = vibe.vibe_score >= 8 ? "🔥" : vibe.vibe_score >= 5 ? "✨" : "🌙";
  const minsRaw = distance_km != null ? Math.max(1, Math.round((distance_km / 5) * 60)) : null;
  const distLine = minsRaw ? `${minsRaw} min away` : "Nearby";
  const cat = {
    club: "Live DJ",
    bar: "Chill Vibes",
    live_music: "Live Band",
  }[venue.category] || "Vibes";
  const params = new URLSearchParams({ v: venue.id });
  if (myUserId) params.set("ref", myUserId);
  const link = `${window.location.origin}/?${params.toString()}`;
  const text =
    `${flame} ${venue.name} is a ${score} vibe right now\n` +
    `📍 ${distLine} · ${cat}\n` +
    `Find tonight's vibe → ${link}`;
  return { title: `${venue.name} · Vibe ${score}`, text, url: link };
}

export default function Home() {
  const navigate = useNavigate();
  const [loc, setLoc] = useState(DEFAULT_LOCATION);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [radius, setRadius] = useState(50);
  const [tab, setTab] = useState("home");
  const [claimVenue, setClaimVenue] = useState(null);
  const [fvvBadge, setFvvBadge] = useState(null);
  const toast = useToast();

  // Stable anonymous identity for this device — used as wallet user_id
  // and as the referrer parameter on share links.
  const myUserId = useMemo(() => getOrCreateUserId(), []);

  // On first mount, snatch ?ref=<inviter-id> from the URL (if present) and
  // clean the param. We'll honour it on the user's first credit-eligible
  // action below.
  useEffect(() => {
    capturePendingReferrer();
  }, []);

  // Poll my own wallet every 30s — when referral_credits ticks up,
  // celebrate with a toast on the Home page itself. Auto-pauses when the
  // tab is hidden; resumes immediately on focus.
  useReferralPing(myUserId, toast, 30000);

  // Best-effort: if a pending referrer exists, credit them +5 Vibe Credits
  // on the recipient's first credit-eligible action. Fires at most once
  // per device (consume clears the storage key).
  const honourPendingReferral = useCallback(async () => {
    const inviter = consumePendingReferrer();
    if (!inviter) return;
    try {
      await earnReward(inviter, "referral");
      toast.success("+5 Vibe Credits sent to whoever invited you 💜");
    } catch {
      // Re-stash so we can retry on a future action — but only if storage works.
      // (Intentionally ignored — losing one referral credit isn't fatal.)
    }
  }, [toast]);

  const getDeviceId = () => {
    // Implementation here
  };

  const onCheckIn = async (venue) => {
    // Implementation here
  };

  const useMyLocation = () => {
    // Implementation here
  };

  const handleVote = async (venue_id, vote) => {
    // Implementation here
  };

  // Render based on state
  if (loading) return <LoadingScreen />;
  if (error) return <ErrorState message={error} />;
  if (!data?.length) return <EmptyState />;

  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-purple-900/20 to-black">
      <Navbar rightSlot={<Locate size={18} />} />
      {/* Content here */}
      <Footer />
    </div>
  );
}

function ClaimModal({ venue, onClose, onSuccess }) {
  const submit = async () => {
    // Implementation here
  };

  return (
    <Modal open onClose={onClose}>
      {/* Modal content */}
    </Modal>
  );
}
