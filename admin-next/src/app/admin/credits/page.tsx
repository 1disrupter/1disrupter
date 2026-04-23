"use client";
import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Coins, Plus, Trash2, History } from "lucide-react";
import { Topbar } from "@/components/Sidebar";
import { Button, Chip, Input, Select } from "@/components/ui";
import {
  createRewardOffer,
  deactivateRewardOffer,
  getRewardRules,
  listAdminVenues,
  listOffers,
  listRedemptions,
  RewardOffer,
} from "@/lib/api";

export default function CreditsPage() {
  const qc = useQueryClient();
  const [showCreate, setShowCreate] = useState(false);

  const venuesQ = useQuery({ queryKey: ["admin-venues"], queryFn: listAdminVenues });
  const rulesQ = useQuery({ queryKey: ["reward-rules"], queryFn: getRewardRules });
  const offersQ = useQuery({
    queryKey: ["offers"],
    queryFn: () => listOffers(undefined, false),
  });
  const redQ = useQuery({
    queryKey: ["redemptions"],
    queryFn: () => listRedemptions({ limit: 50 }),
  });

  const venueName = useMemo(() => {
    const m = new Map<string, string>();
    (venuesQ.data?.items ?? []).forEach((v) => m.set(v.venue.id, v.venue.name));
    return m;
  }, [venuesQ.data]);

  const issued = useMemo(() => {
    const items = redQ.data ?? [];
    return items.reduce((s, r) => s + r.cost_credits, 0);
  }, [redQ.data]);

  const deactivate = useMutation({
    mutationFn: (id: string) => deactivateRewardOffer(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["offers"] }),
  });

  return (
    <>
      <Topbar
        title="VIBE CREDITS"
        rightSlot={
          <>
            <Chip tone="amber">
              <Coins size={12} /> {offersQ.data?.length ?? 0} offers
            </Chip>
            <Chip tone="aqua">
              <History size={12} /> {redQ.data?.length ?? 0} redemptions
            </Chip>
            <Button
              variant="pink"
              size="sm"
              leftIcon={<Plus size={14} />}
              onClick={() => setShowCreate(true)}
              data-testid="credits-new-offer-btn"
            >
              New offer
            </Button>
          </>
        }
      />
      <main className="flex-1 space-y-6 p-6">
        {/* Stat tiles */}
        <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
          <StatTile label="Active offers" value={(offersQ.data ?? []).filter((o) => o.active).length} tone="from-primary/25 to-primary-glow/10 border-primary-glow/40" />
          <StatTile label="Redemptions" value={redQ.data?.length ?? 0} tone="from-accent-pink/25 to-accent-magenta/10 border-accent-pink/40" />
          <StatTile label="Credits redeemed" value={issued} tone="from-glow-aqua/25 to-glow-teal/10 border-glow-aqua/40" />
          <StatTile label="Earn rules" value={Object.keys(rulesQ.data ?? {}).length} tone="from-status-busy/25 to-status-busy/5 border-status-busy/40" />
        </div>

        {/* Rules panel */}
        <Panel title="Earn rules (config)">
          <div className="flex flex-wrap gap-2">
            {Object.entries(rulesQ.data ?? {}).map(([k, v]) => (
              <Chip key={k} tone="purple">
                {k.replace(/_/g, " ")} <span className="ml-1 font-mono text-glow-aqua">+{v}</span>
              </Chip>
            ))}
          </div>
        </Panel>

        {/* Offers */}
        <Panel title="Reward offers">
          <div className="overflow-hidden rounded-xl border border-white/10">
            <table className="w-full text-sm" data-testid="offers-table">
              <thead className="bg-white/[0.03] text-[11px] uppercase tracking-[0.22em] text-white/60">
                <tr>
                  <th className="px-4 py-2 text-left">Venue</th>
                  <th className="px-4 py-2 text-left">Offer</th>
                  <th className="px-4 py-2 text-right">Cost</th>
                  <th className="px-4 py-2 text-center">Status</th>
                  <th className="px-4 py-2" />
                </tr>
              </thead>
              <tbody>
                {(offersQ.data ?? []).map((o) => (
                  <tr key={o.id} className="border-t border-white/5 text-white/85">
                    <td className="px-4 py-2">{venueName.get(o.venue_id) || o.venue_id.slice(0, 8)}</td>
                    <td className="px-4 py-2">
                      <div className="font-semibold">{o.name}</div>
                      {o.description && <div className="text-xs text-white/55">{o.description}</div>}
                    </td>
                    <td className="px-4 py-2 text-right font-mono text-glow-aqua">{o.cost_credits}</td>
                    <td className="px-4 py-2 text-center">
                      <Chip tone={o.active ? "aqua" : "neutral"}>{o.active ? "Active" : "Retired"}</Chip>
                    </td>
                    <td className="px-4 py-2 text-right">
                      {o.active && (
                        <button
                          onClick={() => deactivate.mutate(o.id)}
                          className="inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs text-white/60 hover:text-accent-pink hover:bg-white/5"
                          data-testid={`retire-offer-${o.id}`}
                        >
                          <Trash2 size={12} /> Retire
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
                {(offersQ.data ?? []).length === 0 && (
                  <tr><td colSpan={5} className="px-4 py-10 text-center text-white/50">No offers yet. Create one to let users spend credits.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </Panel>

        {/* Recent redemptions */}
        <Panel title="Recent redemptions">
          <div className="overflow-hidden rounded-xl border border-white/10">
            <table className="w-full text-sm" data-testid="redemptions-table">
              <thead className="bg-white/[0.03] text-[11px] uppercase tracking-[0.22em] text-white/60">
                <tr>
                  <th className="px-4 py-2 text-left">When</th>
                  <th className="px-4 py-2 text-left">Venue</th>
                  <th className="px-4 py-2 text-left">User</th>
                  <th className="px-4 py-2 text-right">Cost</th>
                </tr>
              </thead>
              <tbody>
                {(redQ.data ?? []).map((r) => (
                  <tr key={r.id} className="border-t border-white/5 text-white/85">
                    <td className="px-4 py-2 font-mono text-xs text-white/60">{new Date(r.timestamp).toLocaleString()}</td>
                    <td className="px-4 py-2">{venueName.get(r.venue_id) || r.venue_id.slice(0, 8)}</td>
                    <td className="px-4 py-2 font-mono text-xs text-white/70">{r.user_id.slice(0, 12)}…</td>
                    <td className="px-4 py-2 text-right font-mono text-glow-aqua">{r.cost_credits}</td>
                  </tr>
                ))}
                {(redQ.data ?? []).length === 0 && (
                  <tr><td colSpan={4} className="px-4 py-10 text-center text-white/50">No redemptions yet.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </Panel>
      </main>

      {showCreate && (
        <CreateOfferModal
          venues={(venuesQ.data?.items ?? []).map((v) => v.venue)}
          onClose={() => setShowCreate(false)}
          onCreated={() => {
            qc.invalidateQueries({ queryKey: ["offers"] });
            setShowCreate(false);
          }}
        />
      )}
    </>
  );
}

function StatTile({ label, value, tone }: { label: string; value: number | string; tone: string }) {
  return (
    <div className={`rounded-xl2 border bg-gradient-to-br p-4 ${tone}`}>
      <p className="text-[11px] uppercase tracking-[0.22em] text-white/60">{label}</p>
      <p className="mt-2 font-display text-4xl tracking-wider text-white">{value}</p>
    </div>
  );
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="space-y-3 rounded-xl2 border border-white/10 bg-white/[0.02] p-5">
      <h3 className="text-[11px] uppercase tracking-[0.28em] text-white/55">{title}</h3>
      {children}
    </section>
  );
}

function CreateOfferModal({
  venues, onClose, onCreated,
}: {
  venues: { id: string; name: string }[];
  onClose: () => void;
  onCreated: (o: RewardOffer) => void;
}) {
  const [venue_id, setVenueId] = useState(venues[0]?.id ?? "");
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [cost, setCost] = useState(5);

  const create = useMutation({
    mutationFn: () => createRewardOffer({ venue_id, name, cost_credits: cost, description }),
    onSuccess: (o) => onCreated(o),
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-[#05050A]/80 backdrop-blur-md" onClick={onClose} />
      <div className="relative w-full max-w-lg rounded-xl3 border border-primary-glow/30 bg-background-dark p-6 shadow-softPurple" data-testid="create-offer-modal">
        <h2 className="mb-4 font-display text-2xl tracking-wider text-white">NEW OFFER</h2>
        <div className="space-y-3">
          <Select label="Venue" value={venue_id} onChange={(e) => setVenueId(e.target.value)} data-testid="offer-venue-select">
            {venues.map((v) => <option key={v.id} value={v.id}>{v.name}</option>)}
          </Select>
          <Input label="Offer name" value={name} onChange={(e) => setName(e.target.value)} placeholder="Free shot" data-testid="offer-name-input" />
          <Input label="Description" value={description} onChange={(e) => setDescription(e.target.value)} placeholder="One free house shot per visit" />
          <Input label="Cost (credits)" type="number" min={1} value={cost} onChange={(e) => setCost(Number(e.target.value))} data-testid="offer-cost-input" />
        </div>
        <div className="mt-5 flex justify-end gap-3">
          <Button variant="secondary" onClick={onClose}>Cancel</Button>
          <Button
            variant="pink"
            loading={create.isPending}
            disabled={!venue_id || !name || cost < 1}
            onClick={() => create.mutate()}
            data-testid="create-offer-submit"
          >
            Create
          </Button>
        </div>
      </div>
    </div>
  );
}
