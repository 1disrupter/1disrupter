"use client";
import { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Search, RefreshCw } from "lucide-react";
import {
  listAdminVenues, createVenue, triggerSignalRefresh, AdminVenueRow, Category,
} from "@/lib/api";
import { Topbar } from "@/components/Sidebar";
import { Button, Chip, Input, Select } from "@/components/ui";
import { InspectorModal } from "@/components/InspectorModal";
import { cn } from "@/lib/cn";

export default function VenuesPage() {
  const qc = useQueryClient();
  const q = useQuery({ queryKey: ["admin-venues"], queryFn: listAdminVenues });
  const refresh = useMutation({
    mutationFn: triggerSignalRefresh,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-venues"] }),
  });
  const [query, setQuery] = useState("");
  const [inspect, setInspect] = useState<AdminVenueRow | null>(null);
  const [addOpen, setAddOpen] = useState(false);

  const rows = useMemo(
    () => (q.data?.items ?? []).filter((r) => r.venue.name.toLowerCase().includes(query.toLowerCase())),
    [q.data, query]
  );

  const catTone = (c: Category) => c === "live_music" ? "pink" : c === "club" ? "purple" : "aqua";

  return (
    <>
      <Topbar
        title="VENUES"
        rightSlot={
          <>
            <Chip tone="purple">Live</Chip>
            <Chip>{rows.length} rows</Chip>
            <Button
              variant="secondary" size="sm"
              leftIcon={<RefreshCw size={14} className={refresh.isPending ? "animate-spin" : ""} />}
              onClick={() => refresh.mutate()}
            >
              {refresh.isPending ? "Refreshing…" : "Refresh"}
            </Button>
          </>
        }
      />
      <main className="flex-1 space-y-4 p-6">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 flex-1 rounded-full border border-white/10 bg-white/5 px-4 py-2.5 focus-within:border-primary-glow/60">
            <Search size={16} className="text-primary-glow" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search venues…"
              className="flex-1 bg-transparent text-sm text-white outline-none placeholder:text-white/40"
            />
          </div>
          <Button variant="pink" leftIcon={<Plus size={14} />} onClick={() => setAddOpen(true)}>
            Add venue
          </Button>
        </div>

        <div className="overflow-hidden rounded-xl2 border border-white/10">
          <table className="min-w-full text-sm">
            <thead className="bg-white/[0.03] text-left text-[11px] uppercase tracking-[0.22em] text-white/55">
              <tr>
                <th className="p-3">Name</th>
                <th className="p-3">Category</th>
                <th className="p-3">Score</th>
                <th className="p-3">Crowd</th>
                <th className="p-3">Lat / Lng</th>
                <th className="p-3"></th>
              </tr>
            </thead>
            <tbody>
              {q.isLoading && (
                <tr><td colSpan={6} className="p-8 text-center text-white/55">Loading…</td></tr>
              )}
              {q.error && (
                <tr><td colSpan={6} className="p-8 text-center text-accent-pink">{String((q.error as Error).message)}</td></tr>
              )}
              {rows.map((r, i) => (
                <tr key={r.venue.id} className={cn("border-t border-white/5", i % 2 ? "bg-white/[0.01]" : "")}>
                  <td className="p-3 font-semibold text-white">{r.venue.name}</td>
                  <td className="p-3"><Chip tone={catTone(r.venue.category) as any}>{r.venue.category.replace("_", " ")}</Chip></td>
                  <td className="p-3 font-mono text-primary-glow">{r.vibe.vibe_score.toFixed(2)}</td>
                  <td className="p-3">
                    <CrowdPill level={r.vibe.crowd_level} />
                  </td>
                  <td className="p-3 font-mono text-xs text-white/55">
                    {r.venue.latitude.toFixed(3)}, {r.venue.longitude.toFixed(3)}
                  </td>
                  <td className="p-3 text-right">
                    <Button size="sm" variant="secondary" onClick={() => setInspect(r)}>Inspect</Button>
                  </td>
                </tr>
              ))}
              {!q.isLoading && !q.error && !rows.length && (
                <tr><td colSpan={6} className="p-10 text-center text-white/55">No venues match.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </main>

      {inspect && (
        <InspectorModal
          row={inspect}
          onClose={() => setInspect(null)}
          onSaved={() => qc.invalidateQueries({ queryKey: ["admin-venues"] })}
        />
      )}
      <AddVenueModal open={addOpen} onClose={() => setAddOpen(false)} onCreated={() => qc.invalidateQueries({ queryKey: ["admin-venues"] })} />
    </>
  );
}

function CrowdPill({ level }: { level: "busy" | "medium" | "dead" }) {
  const m = {
    busy: { color: "bg-status-busy shadow-[0_0_10px_#FF9A1F]", label: "Busy" },
    medium: { color: "bg-status-medium", label: "Medium" },
    dead: { color: "bg-status-dead", label: "Dead" },
  }[level];
  return (
    <span className="inline-flex items-center gap-2 text-xs font-medium uppercase tracking-widest text-white/85">
      <span className={cn("h-2 w-2 rounded-full", m.color)} />
      {m.label}
    </span>
  );
}

function AddVenueModal({ open, onClose, onCreated }: { open: boolean; onClose: () => void; onCreated: () => void }) {
  const [name, setName] = useState("");
  const [category, setCategory] = useState<Category>("bar");
  const [lat, setLat] = useState(40.73);
  const [lng, setLng] = useState(-73.99);
  const [err, setErr] = useState("");
  const create = useMutation({
    mutationFn: () => createVenue({ name, category, latitude: lat, longitude: lng }),
    onSuccess: () => { onCreated(); onClose(); setName(""); },
    onError: (e: Error) => setErr(e.message),
  });
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#05050A]/80 backdrop-blur-md">
      <div className="w-full max-w-lg rounded-xl3 border border-primary-glow/30 bg-background-dark p-6 shadow-softPurple">
        <h3 className="font-display text-2xl tracking-wider text-white mb-4">NEW VENUE</h3>
        <div className="grid gap-4 md:grid-cols-2">
          <Input label="Name" value={name} onChange={(e) => setName(e.target.value)} />
          <Select label="Category" value={category} onChange={(e) => setCategory(e.target.value as Category)}>
            <option value="bar">Bar</option>
            <option value="club">Club</option>
            <option value="live_music">Live Music</option>
          </Select>
          <Input label="Latitude" type="number" value={lat} onChange={(e) => setLat(Number(e.target.value))} />
          <Input label="Longitude" type="number" value={lng} onChange={(e) => setLng(Number(e.target.value))} />
        </div>
        {err && <p className="mt-3 text-sm text-accent-pink">{err}</p>}
        <div className="mt-5 flex justify-end gap-3">
          <Button variant="secondary" onClick={onClose}>Cancel</Button>
          <Button variant="primary" onClick={() => { setErr(""); if (!name.trim()) return setErr("Name required"); create.mutate(); }} loading={create.isPending}>Create</Button>
        </div>
      </div>
    </div>
  );
}
