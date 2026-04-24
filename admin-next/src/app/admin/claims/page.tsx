"use client";
import { useMemo, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { RefreshCw, Radar, Activity, ShieldCheck } from "lucide-react";
import { Topbar } from "@/components/Sidebar";
import { Button, Chip } from "@/components/ui";
import { cn } from "@/lib/cn";
import {
  listClaims, reviewClaim, getProviderStatus, getRecentWebhooks,
  type ClaimStatus, type VenueClaim,
} from "@/lib/api";

const FILTERS: (ClaimStatus | "")[] = ["", "pending", "email_sent", "verified", "rejected"];

export default function ClaimsPage() {
  const qc = useQueryClient();
  const [filter, setFilter] = useState<ClaimStatus | "">("");

  const claimsQ = useQuery({
    queryKey: ["admin-claims", filter],
    queryFn: () => listClaims(filter || undefined),
  });
  const providersQ = useQuery({
    queryKey: ["admin-providers"],
    queryFn: getProviderStatus,
  });
  const webhooksQ = useQuery({
    queryKey: ["admin-webhooks"],
    queryFn: () => getRecentWebhooks(20),
    refetchInterval: 30_000,
  });

  const review = useMutation({
    mutationFn: ({ id, action }: { id: string; action: "approve" | "reject" }) =>
      reviewClaim(id, action, "admin"),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin-claims"] });
      qc.invalidateQueries({ queryKey: ["admin-webhooks"] });
    },
  });

  const claims = claimsQ.data?.items ?? [];
  const providers = providersQ.data?.providers ?? [];
  const webhooks = webhooksQ.data ?? { configured: {}, recent: [] };

  const statusTone = (s: ClaimStatus): "neutral" | "purple" | "aqua" | "pink" =>
    (({ pending: "neutral", email_sent: "purple", verified: "aqua", rejected: "pink" } as const)[s] || "neutral");

  const anyConfigured = useMemo(
    () => Object.values(webhooks.configured).some(Boolean),
    [webhooks.configured]
  );

  return (
    <>
      <Topbar
        title="CLAIMS"
        rightSlot={
          <>
            <Chip tone="purple">admin-only</Chip>
            <Button
              variant="secondary"
              size="sm"
              leftIcon={<RefreshCw size={14} />}
              onClick={() => {
                claimsQ.refetch();
                providersQ.refetch();
                webhooksQ.refetch();
              }}
            >
              Refresh
            </Button>
          </>
        }
      />

      <main className="flex-1 space-y-6 p-6" data-testid="next-admin-claims">
        {/* Filter chips */}
        <div className="flex flex-wrap gap-2">
          {FILTERS.map((k) => (
            <button
              key={k || "all"}
              onClick={() => setFilter(k)}
              data-testid={`next-claims-filter-${k || "all"}`}
              className={cn(
                "inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs uppercase tracking-[0.22em] transition",
                filter === k
                  ? "border-primary-glow/60 bg-primary/15 text-white"
                  : "border-white/10 text-white/55 hover:text-white hover:bg-white/5"
              )}
            >
              {k || "all"}
            </button>
          ))}
        </div>

        {/* Provider status */}
        <div className="rounded-xl2 border border-white/10 bg-white/[0.02] p-4" data-testid="next-providers-panel">
          <div className="mb-3 flex items-center gap-2 text-[11px] uppercase tracking-[0.28em] text-primary-glow">
            <Radar size={12} /> Provider status
          </div>
          <ul className="grid gap-2 md:grid-cols-2">
            {providers.map((p) => (
              <li
                key={p.provider}
                data-testid={`next-provider-${p.provider}`}
                className="flex items-center justify-between rounded-xl border border-white/10 bg-white/[0.02] px-3 py-2 text-sm"
              >
                <div className="flex items-center gap-2">
                  <Chip tone={p.mode === "live" ? "aqua" : "neutral"}>{p.mode}</Chip>
                  <span className="text-white">{p.provider}</span>
                  <span className="text-[11px] uppercase tracking-[0.2em] text-white/45">{p.category}</span>
                </div>
                <code className="text-[11px] text-white/45">{p.env_var}</code>
              </li>
            ))}
          </ul>
        </div>

        {/* Webhook log */}
        <div className="rounded-xl2 border border-white/10 bg-white/[0.02] p-4" data-testid="next-webhooks-panel">
          <div className="mb-3 flex items-center gap-2 text-[11px] uppercase tracking-[0.28em] text-primary-glow">
            <Activity size={12} /> Webhook events
            <span className="ml-auto text-white/45">
              {Object.entries(webhooks.configured).map(([k, v]) => (
                <span key={k} className={cn("ml-2", v ? "text-glow-aqua" : "text-white/35")}>
                  {k}:{v ? "on" : "off"}
                </span>
              ))}
            </span>
          </div>
          {webhooks.recent.length === 0 ? (
            <p className="text-xs text-white/45">
              No recent events. Dispatcher is {anyConfigured ? "armed" : "idle (no URL configured)"}.
            </p>
          ) : (
            <ul className="space-y-1.5 text-xs">
              {webhooks.recent.map((e, i) => (
                <li key={i} className="flex items-center gap-2">
                  <Chip tone={e.ok ? "aqua" : "pink"}>{e.event_type}</Chip>
                  <span className="text-white/80">{e.title}</span>
                  {!e.ok && <span className="text-accent-pink">· {e.error}</span>}
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Claims table */}
        <div className="overflow-hidden rounded-xl2 border border-white/10">
          <table className="min-w-full text-sm">
            <thead className="bg-white/[0.03] text-left text-[11px] uppercase tracking-[0.22em] text-white/55">
              <tr>
                <th className="p-3">Venue</th>
                <th className="p-3">Owner</th>
                <th className="p-3">Status</th>
                <th className="p-3">Proof</th>
                <th className="p-3">Submitted</th>
                <th className="p-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {claimsQ.isLoading ? (
                <tr><td colSpan={6} className="p-6 text-center text-xs text-white/45">Loading…</td></tr>
              ) : claims.length === 0 ? (
                <tr><td colSpan={6} className="p-10 text-center text-white/45">
                  <div className="flex flex-col items-center gap-2">
                    <ShieldCheck size={28} className="text-primary-glow" />
                    <p className="text-sm">No claims {filter ? `with status "${filter}"` : "yet"}.</p>
                  </div>
                </td></tr>
              ) : claims.map((c: VenueClaim, i: number) => (
                <tr key={c.id} className={cn("border-t border-white/5", i % 2 ? "bg-white/[0.01]" : "")} data-testid={`next-claim-row-${c.id}`}>
                  <td className="p-3 font-mono text-[11px] text-white/70">{c.venue_id.slice(0, 8)}…</td>
                  <td className="p-3">
                    <div className="text-white">{c.owner_name}</div>
                    <div className="text-[11px] text-white/50">{c.email}</div>
                  </td>
                  <td className="p-3"><Chip tone={statusTone(c.status)}>{c.status.replace("_", " ")}</Chip></td>
                  <td className="p-3 max-w-[220px] truncate text-xs text-glow-aqua">
                    {c.proof ? <a href={c.proof} target="_blank" rel="noreferrer">{c.proof}</a> : "—"}
                  </td>
                  <td className="p-3 font-mono text-[11px] text-white/55">
                    {new Date(c.created_at).toLocaleString()}
                  </td>
                  <td className="p-3 text-right">
                    {c.status === "verified" || c.status === "rejected" ? (
                      <span className="text-[11px] text-white/35">
                        {c.reviewed_at ? `reviewed ${new Date(c.reviewed_at).toLocaleString()}` : "self-verified"}
                      </span>
                    ) : (
                      <div className="flex justify-end gap-2">
                        <Button
                          size="sm" variant="secondary"
                          onClick={() => review.mutate({ id: c.id, action: "reject" })}
                          disabled={review.isPending}
                          data-testid={`next-claim-reject-${c.id}`}
                        >Reject</Button>
                        <Button
                          size="sm" variant="pink"
                          onClick={() => review.mutate({ id: c.id, action: "approve" })}
                          disabled={review.isPending}
                          data-testid={`next-claim-approve-${c.id}`}
                        >Approve</Button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </main>
    </>
  );
}
