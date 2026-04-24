"use client";
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Rocket, QrCode, Plus, Trash2, Copy, Globe, Sparkles, Check, XIcon } from "lucide-react";
import { Topbar } from "@/components/Sidebar";
import { Button, Chip, Input, Select } from "@/components/ui";
import {
  getLocalGems, listAdminVenues, onboardVenue, seedCity, CitySeedVenue,
  osmPreview, osmImport, OsmCandidate,
  getNewVenues, getClosedVenues, getTrendingVenues, approveCandidate, rejectCandidate,
} from "@/lib/api";

type SeedDraft = CitySeedVenue & { id: string };

function blankVenue(): SeedDraft {
  return {
    id: Math.random().toString(36).slice(2),
    name: "",
    category: "bar",
    latitude: 36.595,
    longitude: -4.516,
    music_type: "",
    price_level: 2,
    age_group: "21+",
    dress_code: "",
    photos: [],
  };
}

export default function LaunchModePage() {
  const qc = useQueryClient();
  const venuesQ = useQuery({ queryKey: ["admin-venues"], queryFn: listAdminVenues });
  const gemsQ = useQuery({ queryKey: ["local-gems"], queryFn: () => getLocalGems(10) });

  const [city, setCity] = useState("Benalmádena");
  const [drafts, setDrafts] = useState<SeedDraft[]>([blankVenue()]);

  const seedM = useMutation({
    mutationFn: () => seedCity(city, drafts.map(({ id, ...rest }) => rest)),
    onSuccess: (res) => {
      qc.invalidateQueries({ queryKey: ["admin-venues"] });
      alert(`Seeded ${res.total} venues — ${res.created} new, ${res.updated} updated.`);
    },
  });

  return (
    <>
      <Topbar
        title="LAUNCH MODE"
        rightSlot={
          <>
            <Chip tone="purple"><Rocket size={12} /> {venuesQ.data?.count ?? 0} venues</Chip>
            <Chip tone="aqua">{gemsQ.data?.items.length ?? 0} gems</Chip>
          </>
        }
      />
      <main className="flex-1 space-y-6 p-6">
        {/* City seed */}
        <section className="space-y-3 rounded-xl2 border border-white/10 bg-white/[0.02] p-5">
          <h3 className="text-[11px] uppercase tracking-[0.28em] text-white/55">City seed</h3>
          <div className="grid gap-3 md:grid-cols-[1fr_auto]">
            <Input label="City name" value={city} onChange={(e) => setCity(e.target.value)} data-testid="seed-city-input" />
            <div className="flex items-end">
              <Button
                variant="pink" size="md"
                leftIcon={<Plus size={14} />}
                onClick={() => setDrafts((d) => [...d, blankVenue()])}
                data-testid="seed-add-row-btn"
              >
                Add venue
              </Button>
            </div>
          </div>

          <div className="mt-3 space-y-3">
            {drafts.map((d, idx) => (
              <div key={d.id} className="grid gap-3 rounded-xl border border-white/10 p-3 md:grid-cols-6">
                <Input label="Name" value={d.name} onChange={(e) => patch(setDrafts, idx, { name: e.target.value })} />
                <Select
                  label="Category" value={d.category}
                  onChange={(e) => patch(setDrafts, idx, { category: e.target.value as any })}
                >
                  <option value="bar">Bar</option>
                  <option value="club">Club</option>
                  <option value="live_music">Live music</option>
                </Select>
                <Input label="Lat" type="number" value={d.latitude}
                       onChange={(e) => patch(setDrafts, idx, { latitude: Number(e.target.value) })} />
                <Input label="Lng" type="number" value={d.longitude}
                       onChange={(e) => patch(setDrafts, idx, { longitude: Number(e.target.value) })} />
                <Input label="Music" value={d.music_type || ""}
                       onChange={(e) => patch(setDrafts, idx, { music_type: e.target.value })} />
                <Input label="Price (1-4)" type="number" min={1} max={4} value={d.price_level ?? 2}
                       onChange={(e) => patch(setDrafts, idx, { price_level: Number(e.target.value) })} />
                <Input label="Age group" value={d.age_group || ""}
                       onChange={(e) => patch(setDrafts, idx, { age_group: e.target.value })} />
                <Input label="Dress code" value={d.dress_code || ""}
                       onChange={(e) => patch(setDrafts, idx, { dress_code: e.target.value })} />
                <div className="flex items-end md:col-span-4">
                  <button
                    onClick={() => setDrafts((s) => s.filter((x) => x.id !== d.id))}
                    className="inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs text-white/60 hover:text-accent-pink hover:bg-white/5"
                  >
                    <Trash2 size={12} /> Remove
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div className="flex justify-end">
            <Button
              variant="pink" size="md"
              leftIcon={<Rocket size={14} />}
              loading={seedM.isPending}
              onClick={() => seedM.mutate()}
              disabled={!drafts.length || drafts.some((d) => !d.name.trim())}
              data-testid="seed-submit-btn"
            >
              Seed {drafts.length} venues
            </Button>
          </div>
        </section>

        {/* OSM importer */}
        <OsmImportPanel />

        {/* Discovery */}
        <DiscoveryPanel />

        {/* Venue onboarding */}
        <OnboardPanel venues={(venuesQ.data?.items ?? []).map((v) => v.venue)} />

        {/* Local gems preview */}
        <section className="space-y-3 rounded-xl2 border border-white/10 bg-white/[0.02] p-5">
          <h3 className="text-[11px] uppercase tracking-[0.28em] text-white/55">Local Gems preview</h3>
          <div className="grid gap-2 md:grid-cols-2">
            {(gemsQ.data?.items ?? []).map((g) => (
              <div key={g.venue_id} className="flex items-center justify-between rounded-xl border border-glow-aqua/25 bg-glow-aqua/5 px-4 py-2">
                <span className="text-white/85">{g.name}</span>
                <span className="font-mono text-glow-aqua">{g.vibe_score.toFixed(1)} · gem {g.gem_score.toFixed(2)}</span>
              </div>
            ))}
            {(gemsQ.data?.items ?? []).length === 0 && (
              <p className="text-xs text-white/50">No gems yet. Vote on a few venues + wait for the classifier to run.</p>
            )}
          </div>
        </section>
      </main>
    </>
  );
}

function patch<T>(setter: React.Dispatch<React.SetStateAction<T[]>>, idx: number, delta: Partial<T>) {
  setter((rows) => rows.map((r, i) => (i === idx ? { ...r, ...delta } : r)));
}

function OsmImportPanel() {
  const [city, setCity] = useState("Benalmádena");
  const [preview, setPreview] = useState<OsmCandidate[] | null>(null);
  const [overwrite, setOverwrite] = useState(false);

  const previewM = useMutation({
    mutationFn: () => osmPreview({ city, limit: 50 }),
    onSuccess: (r) => setPreview(r.candidates),
  });
  const importM = useMutation({
    mutationFn: () => osmImport({ city, overwrite, limit: 500 }),
    onSuccess: (r) => {
      alert(`Imported ${r.imported_count} new, ${r.updated_count} updated, ${r.skipped_count} skipped.`);
      setPreview(null);
    },
  });

  return (
    <section className="space-y-3 rounded-xl2 border border-glow-aqua/30 bg-glow-aqua/5 p-5" data-testid="osm-import-panel">
      <div className="flex items-center justify-between">
        <h3 className="text-[11px] uppercase tracking-[0.28em] text-white/55">
          <Globe size={12} className="inline mr-1" /> OpenStreetMap importer
        </h3>
        <Chip tone="aqua">Legal · Free · Global</Chip>
      </div>
      <div className="grid gap-3 md:grid-cols-[1fr_auto_auto_auto]">
        <Input label="City" value={city} onChange={(e) => setCity(e.target.value)} data-testid="osm-city-input" />
        <div className="flex items-end">
          <label className="flex items-center gap-2 text-[11px] uppercase tracking-[0.22em] text-white/60">
            <input type="checkbox" checked={overwrite} onChange={(e) => setOverwrite(e.target.checked)} />
            Overwrite
          </label>
        </div>
        <div className="flex items-end">
          <Button
            variant="secondary" size="md" leftIcon={<Sparkles size={14} />}
            loading={previewM.isPending} onClick={() => previewM.mutate()}
            disabled={!city.trim()}
            data-testid="osm-preview-btn"
          >
            Preview
          </Button>
        </div>
        <div className="flex items-end">
          <Button
            variant="pink" size="md" leftIcon={<Rocket size={14} />}
            loading={importM.isPending} onClick={() => importM.mutate()}
            disabled={!preview || preview.length === 0}
            data-testid="osm-import-btn"
          >
            Import {preview?.length ?? 0}
          </Button>
        </div>
      </div>

      {preview && preview.length > 0 && (
        <div className="mt-2 max-h-64 overflow-auto rounded-xl border border-white/10">
          <table className="w-full text-xs" data-testid="osm-preview-table">
            <thead className="bg-white/[0.04] text-[10px] uppercase tracking-[0.22em] text-white/55">
              <tr>
                <th className="px-3 py-2 text-left">Name</th>
                <th className="px-3 py-2 text-left">Category</th>
                <th className="px-3 py-2 text-left">Coords</th>
                <th className="px-3 py-2 text-left">Hours</th>
              </tr>
            </thead>
            <tbody>
              {preview.map((c) => (
                <tr key={c.osm_id} className="border-t border-white/5 text-white/85">
                  <td className="px-3 py-2">{c.name}</td>
                  <td className="px-3 py-2">
                    <Chip tone="purple">{c.category}</Chip>
                  </td>
                  <td className="px-3 py-2 font-mono text-white/60">{c.lat.toFixed(3)}, {c.lng.toFixed(3)}</td>
                  <td className="px-3 py-2 text-white/55">{c.opening_hours_raw || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {preview && preview.length === 0 && (
        <p className="text-xs text-white/55">No OSM matches — try a larger city or a different spelling.</p>
      )}
    </section>
  );
}

function DiscoveryPanel() {
  const qc = useQueryClient();
  const [city, setCity] = useState("Benalmádena");

  const newQ = useQuery({ queryKey: ["discovery-new", city], queryFn: () => getNewVenues(city), enabled: !!city });
  const closedQ = useQuery({ queryKey: ["discovery-closed", city], queryFn: () => getClosedVenues(city), enabled: !!city });
  const trendingQ = useQuery({ queryKey: ["discovery-trending", city], queryFn: () => getTrendingVenues(city, 10) });

  const act = useMutation({
    mutationFn: async (a: { id: string; kind: "approve" | "reject" }) =>
      a.kind === "approve" ? approveCandidate(a.id) : rejectCandidate(a.id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["discovery-new", city] });
      qc.invalidateQueries({ queryKey: ["discovery-closed", city] });
      qc.invalidateQueries({ queryKey: ["admin-venues"] });
    },
  });

  return (
    <section className="space-y-3 rounded-xl2 border border-primary-glow/30 bg-primary/5 p-5" data-testid="discovery-panel">
      <div className="flex items-center justify-between">
        <h3 className="text-[11px] uppercase tracking-[0.28em] text-white/55">
          <Sparkles size={12} className="inline mr-1" /> AI discovery
        </h3>
        <Input label="City" value={city} onChange={(e) => setCity(e.target.value)} className="max-w-[220px]" />
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <DiscoveryColumn
          title={`New (${newQ.data?.items.length ?? 0})`}
          tone="aqua"
          items={newQ.data?.items ?? []}
          onApprove={(id) => act.mutate({ id, kind: "approve" })}
          onReject={(id) => act.mutate({ id, kind: "reject" })}
          testPrefix="discovery-new"
        />
        <DiscoveryColumn
          title={`Closed (${closedQ.data?.items.length ?? 0})`}
          tone="pink"
          items={closedQ.data?.items ?? []}
          onApprove={(id) => act.mutate({ id, kind: "approve" })}
          onReject={(id) => act.mutate({ id, kind: "reject" })}
          testPrefix="discovery-closed"
        />
        <DiscoveryColumn
          title={`Trending (${trendingQ.data?.items.length ?? 0})`}
          tone="purple"
          items={trendingQ.data?.items ?? []}
          onApprove={() => null}
          onReject={() => null}
          showActions={false}
          testPrefix="discovery-trending"
        />
      </div>
    </section>
  );
}

function DiscoveryColumn({
  title, tone, items, onApprove, onReject, showActions = true, testPrefix,
}: {
  title: string;
  tone: "aqua" | "pink" | "purple";
  items: { id: string; name: string; reason: string; confidence?: number; score?: number }[];
  onApprove: (id: string) => void;
  onReject: (id: string) => void;
  showActions?: boolean;
  testPrefix: string;
}) {
  return (
    <div className="rounded-xl border border-white/10 p-3" data-testid={testPrefix}>
      <div className="mb-2 flex items-center justify-between">
        <h4 className="text-[11px] uppercase tracking-[0.22em] text-white/55">{title}</h4>
      </div>
      <div className="space-y-2 max-h-64 overflow-auto">
        {items.length === 0 && <p className="text-[11px] text-white/45">Nothing pending.</p>}
        {items.map((i) => (
          <div key={i.id} className="rounded-xl border border-white/10 p-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-white/85 truncate pr-2">{i.name}</span>
              <Chip tone={tone}>{((i.confidence ?? i.score ?? 0) as number).toFixed(2)}</Chip>
            </div>
            <p className="mt-1 text-[11px] text-white/55">{i.reason}</p>
            {showActions && (
              <div className="mt-2 flex gap-2">
                <button
                  onClick={() => onApprove(i.id)}
                  className="inline-flex items-center gap-1 rounded-full px-3 py-1 text-[10px] uppercase tracking-[0.22em] border border-glow-aqua/40 text-glow-aqua hover:bg-glow-aqua/10"
                  data-testid={`${testPrefix}-approve-${i.id}`}
                >
                  <Check size={10} /> Approve
                </button>
                <button
                  onClick={() => onReject(i.id)}
                  className="inline-flex items-center gap-1 rounded-full px-3 py-1 text-[10px] uppercase tracking-[0.22em] border border-white/15 text-white/60 hover:bg-white/5"
                  data-testid={`${testPrefix}-reject-${i.id}`}
                >
                  <XIcon size={10} /> Reject
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function OnboardPanel({ venues }: { venues: { id: string; name: string }[] }) {
  const [venue_id, setVenueId] = useState(venues[0]?.id ?? "");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [result, setResult] = useState<{
    username: string; api_key: string;
    qr_codes: { check_in: string; feedback: string; follow_venue: string };
  } | null>(null);

  const submit = useMutation({
    mutationFn: () => onboardVenue({ venue_id, username, password }),
    onSuccess: (r) => setResult(r),
  });

  return (
    <section className="space-y-3 rounded-xl2 border border-white/10 bg-white/[0.02] p-5">
      <h3 className="text-[11px] uppercase tracking-[0.28em] text-white/55">Venue onboarding</h3>
      <div className="grid gap-3 md:grid-cols-4">
        <Select label="Venue" value={venue_id} onChange={(e) => setVenueId(e.target.value)}>
          {venues.map((v) => <option key={v.id} value={v.id}>{v.name}</option>)}
        </Select>
        <Input label="Username" value={username} onChange={(e) => setUsername(e.target.value)} data-testid="onboard-username" />
        <Input label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} data-testid="onboard-password" />
        <div className="flex items-end">
          <Button
            variant="pink" size="md"
            leftIcon={<QrCode size={14} />}
            loading={submit.isPending}
            disabled={!venue_id || username.length < 3 || password.length < 6}
            onClick={() => submit.mutate()}
            data-testid="onboard-submit-btn"
          >
            Generate QR pack
          </Button>
        </div>
      </div>
      {result && (
        <div className="mt-3 space-y-3 rounded-xl border border-glow-aqua/40 bg-glow-aqua/5 p-4" data-testid="onboard-result">
          <div className="flex items-center gap-3 text-xs text-white/85">
            <Chip tone="aqua">KEY</Chip>
            <code className="font-mono break-all">{result.api_key}</code>
            <button
              onClick={() => navigator.clipboard?.writeText(result.api_key)}
              className="inline-flex items-center gap-1 rounded-full px-2 py-1 text-[10px] text-white/60 hover:text-white hover:bg-white/10"
            >
              <Copy size={10} /> COPY
            </button>
          </div>
          <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
            {Object.entries(result.qr_codes).map(([label, src]) => (
              <div key={label} className="rounded-xl border border-white/10 p-3 text-center">
                <p className="text-[10px] uppercase tracking-[0.22em] text-white/45">{label.replace("_", " ")}</p>
                <img src={src} alt={label} className="mx-auto mt-2 h-40 w-40 rounded bg-white p-2" />
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
