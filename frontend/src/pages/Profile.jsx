import React, { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { Sparkles, Users, Copy, RefreshCw, Trophy, Share2, ArrowLeft } from "lucide-react";
import {
  Navbar, Footer, IconButton, Button, Chip, useToast,
  LoadingScreen, ErrorState,
} from "@/components/v2n";
import { cx } from "@/lib/cx";
import { getWallet } from "@/lib/api";
import { getOrCreateUserId } from "@/lib/userId";

// ---------------------------------------------------------------------------
// /me — Anonymous user wallet + invite leaderboard panel.
// Shows: my credit balance, lifetime referral credits, # of friends invited,
// shareable invite link, and a "copy my id" affordance.
// ---------------------------------------------------------------------------

function StatCard({ label, value, hint, tone = "purple", testId }) {
  const tones = {
    purple: "from-primary/25 to-primary-glow/10 border-primary-glow/40",
    pink:   "from-accent-pink/25 to-accent-magenta/10 border-accent-pink/40",
    aqua:   "from-glow-aqua/25 to-glow-teal/10 border-glow-aqua/40",
  };
  return (
    <div
      data-testid={testId}
      className={cx(
        "rounded-xl2 border bg-gradient-to-br p-5",
        tones[tone]
      )}
    >
      <p className="text-[11px] uppercase tracking-[0.24em] text-white/60">{label}</p>
      <p className="mt-2 font-display text-5xl tracking-wider text-white tabular-nums">
        {value}
      </p>
      {hint && <p className="mt-1.5 text-[11px] text-white/50">{hint}</p>}
    </div>
  );
}

export default function Profile() {
  const navigate = useNavigate();
  const toast = useToast();
  const [me] = useState(() => getOrCreateUserId());
  const [wallet, setWallet] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    if (!me) {
      setError("Local storage is disabled — vibe credits won't persist on this browser.");
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const w = await getWallet(me);
      setWallet(w);
    } catch (e) {
      setError(e.response?.data?.detail || e.message || "Couldn't load your wallet");
    } finally {
      setLoading(false);
    }
  }, [me]);

  useEffect(() => { load(); }, [load]);

  const inviteLink = me
    ? `${window.location.origin}/?ref=${encodeURIComponent(me)}`
    : null;

  const copy = async (text, label = "Copied") => {
    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(text);
      } else {
        const ta = document.createElement("textarea");
        ta.value = text;
        ta.setAttribute("readonly", "");
        ta.style.position = "fixed";
        ta.style.opacity = "0";
        document.body.appendChild(ta);
        ta.select();
        document.execCommand("copy");
        document.body.removeChild(ta);
      }
      toast.success(label);
    } catch {
      toast.error("Couldn't copy. Long-press to select.");
    }
  };

  const shareLink = async () => {
    if (!inviteLink) return;
    const payload = {
      title: "VIBE2NITE — pull up tonight",
      text:
        "Pull up to tonight's best spots with me 🌃 — real-time vibe scores for bars, clubs and live music.\n",
      url: inviteLink,
    };
    try {
      if (navigator.share) {
        await navigator.share(payload);
        return;
      }
    } catch (err) {
      if (err?.name === "AbortError") return;
    }
    copy(`${payload.text}${inviteLink}`, "Invite link copied — paste it anywhere 💜");
  };

  const credits = wallet?.credits ?? 0;
  const invites = wallet?.invites ?? 0;
  const refCredits = wallet?.referral_credits ?? 0;

  // Friendly milestone copy that nudges towards more sharing.
  const milestoneCopy =
    invites === 0
      ? "Share your link to invite your first friend tonight."
      : invites < 5
      ? `${invites} friend${invites === 1 ? "" : "s"} pulled up — keep the streak going.`
      : invites < 20
      ? `${invites} invites in. You're a connector. 🔥`
      : `${invites} invites — official Vibe2Nite ambassador. 👑`;

  return (
    <div className="min-h-screen pb-12">
      <Navbar
        rightSlot={
          <IconButton onClick={load} aria-label="Refresh wallet" data-testid="profile-refresh">
            <RefreshCw size={16} />
          </IconButton>
        }
      />
      <main className="mx-auto max-w-4xl px-4 py-8 md:px-6 md:py-12">
        <button
          onClick={() => navigate("/")}
          data-testid="profile-back"
          className="mb-6 inline-flex items-center gap-1.5 text-xs uppercase tracking-[0.28em] text-white/55 hover:text-white"
        >
          <ArrowLeft size={14} /> back to tonight
        </button>

        <header className="mb-8">
          <p className="text-[11px] uppercase tracking-[0.3em] text-primary-glow">My Vibe Credits</p>
          <h1 className="mt-1 font-display text-4xl tracking-wider text-white md:text-5xl">
            YOUR <span className="text-accent-pink">WALLET</span>
          </h1>
          <p className="mt-2 text-sm text-white/55">
            Anonymous &amp; tied to this device. No account required — just keep using the same browser.
          </p>
        </header>

        {loading ? (
          <LoadingScreen label="Loading your wallet…" />
        ) : error ? (
          <ErrorState message={String(error)} onRetry={load} />
        ) : (
          <>
            {/* Top stats */}
            <section className="grid gap-4 md:grid-cols-3" data-testid="profile-stats">
              <StatCard
                testId="stat-credits"
                tone="purple"
                label="Vibe Credits"
                value={credits}
                hint="Earned from votes, visits & invites."
              />
              <StatCard
                testId="stat-invites"
                tone="pink"
                label="Friends Invited"
                value={invites}
                hint={milestoneCopy}
              />
              <StatCard
                testId="stat-referral-credits"
                tone="aqua"
                label="From Referrals"
                value={`+${refCredits}`}
                hint={`${refCredits ? `${refCredits} of your ${credits} credits came from invites.` : "Share to start earning."}`}
              />
            </section>

            {/* Invite hero */}
            <section
              className="mt-8 rounded-xl2 border border-primary-glow/40 bg-gradient-to-br from-primary/15 to-accent-pink/10 p-5 md:p-7"
              data-testid="invite-card"
            >
              <div className="flex items-center gap-2 text-[11px] uppercase tracking-[0.28em] text-primary-glow">
                <Trophy size={14} /> Pull friends out, earn credits
              </div>
              <h2 className="mt-3 font-display text-2xl tracking-wider text-white md:text-3xl">
                +5 VIBE CREDITS for every friend who joins.
              </h2>
              <p className="mt-2 text-sm text-white/65">
                We'll credit you the moment they take their first action — vote, check-in,
                or claim. No accounts. No hassle. Just real social proof.
              </p>

              <div className="mt-5 flex flex-col items-stretch gap-3 sm:flex-row">
                <div
                  className="flex-1 truncate rounded-xl border border-white/10 bg-background-deep/60 px-4 py-3 font-mono text-xs text-white/75"
                  data-testid="invite-link"
                  title={inviteLink || ""}
                >
                  {inviteLink || "Local storage unavailable"}
                </div>
                <Button
                  variant="secondary"
                  leftIcon={<Copy size={14} />}
                  onClick={() => inviteLink && copy(inviteLink, "Invite link copied 💜")}
                  data-testid="invite-copy"
                  disabled={!inviteLink}
                >
                  Copy link
                </Button>
                <Button
                  variant="pink"
                  leftIcon={<Share2 size={14} />}
                  onClick={shareLink}
                  data-testid="invite-share"
                  disabled={!inviteLink}
                >
                  Share
                </Button>
              </div>
            </section>

            {/* Identity strip */}
            <section className="mt-8 rounded-xl2 border border-white/10 bg-white/[0.02] p-5">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-[11px] uppercase tracking-[0.24em] text-white/55">
                    Your anonymous device id
                  </p>
                  <p
                    className="mt-1 font-mono text-xs text-white/70 break-all"
                    data-testid="profile-uuid"
                  >
                    {me || "—"}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <Chip tone="aqua">no account</Chip>
                  {me && (
                    <IconButton
                      onClick={() => copy(me, "Device ID copied")}
                      aria-label="Copy device id"
                      data-testid="profile-copy-id"
                    >
                      <Copy size={14} />
                    </IconButton>
                  )}
                </div>
              </div>
              <p className="mt-3 text-[11px] text-white/40">
                Save this id somewhere safe if you want to restore your wallet on another device.
                We do not collect any other personal data.
              </p>
            </section>
          </>
        )}
      </main>
      <Footer />
    </div>
  );
}
