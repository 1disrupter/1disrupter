"use client";
import { useMemo, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { RefreshCw } from "lucide-react";
import {
  BarChart, Bar, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, Legend,
} from "recharts";
import { Topbar } from "@/components/Sidebar";
import { Button, Chip } from "@/components/ui";
import { listAdminVenues, triggerSignalRefresh } from "@/lib/api";
import { cn } from "@/lib/cn";

const PIE = ["#8A2BE2", "#FF2EC4", "#00F5FF", "#FF9A1F", "#C7A7FF"];

export default function OverviewPage() {
  const qc = useQueryClient();
  const q = useQuery({ queryKey: ["admin-venues"], queryFn: listAdminVenues });
  const [refreshed, setRefreshed] = useState<string | null>(null);
  const refresh = useMutation({
    mutationFn: triggerSignalRefresh,
    onSuccess: (r) => {
      setRefreshed(`${r.refreshed}/${r.total} refreshed`);
      qc.invalidateQueries({ queryKey: ["admin-venues"] });
    },
  });

  const venues = q.data?.items ?? [];
  const stats = useMemo(() => ({
    total: venues.length,
    avg: venues.length ? (venues.reduce((s, v) => s + v.vibe.vibe_score, 0) / venues.length).toFixed(2) : "0.00",
    busy: venues.filter((v) => v.vibe.crowd_level === "busy").length,
    gems: venues.filter((v) => v.vibe.vibe_score < 5).length,
  }), [venues]);

  const top = useMemo(
    () => [...venues].sort((a, b) => b.vibe.vibe_score - a.vibe.vibe_score).slice(0, 8)
      .map((v) => ({ name: v.venue.name, score: v.vibe.vibe_score })),
    [venues]
  );

  const avgSignals = useMemo(() => {
    if (!venues.length) return [];
    const keys: (keyof (typeof venues[0])["vibe"]["signals"])[] = ["manual_score", "social_activity", "user_votes", "time_prediction", "venue_boost"];
    return keys.map((k) => ({
      name: String(k).replace("_", " "),
      value: Number((venues.reduce((s, v) => s + v.vibe.signals[k], 0) / venues.length).toFixed(2)),
    }));
  }, [venues]);

  const byCategory = useMemo(() => {
    const m: Record<string, number> = {};
    venues.forEach((v) => m[v.venue.category] = (m[v.venue.category] || 0) + 1);
    return Object.entries(m).map(([name, value]) => ({ name, value }));
  }, [venues]);

  const byCrowd = useMemo(() => {
    const m = { busy: 0, medium: 0, dead: 0 };
    venues.forEach((v) => (m[v.vibe.crowd_level] = (m[v.vibe.crowd_level] || 0) + 1));
    return Object.entries(m).map(([name, value]) => ({ name, value }));
  }, [venues]);

  const statTones = [
    "from-primary/25 to-primary-glow/10 border-primary-glow/40",
    "from-accent-pink/25 to-accent-magenta/10 border-accent-pink/40",
    "from-glow-aqua/25 to-glow-teal/10 border-glow-aqua/40",
    "from-status-busy/25 to-status-busy/5 border-status-busy/40",
  ];
  const items = [
    ["Venues tracked", stats.total],
    ["Average score", stats.avg],
    ["Currently busy", stats.busy],
    ["Hidden gems", stats.gems],
  ] as const;

  return (
    <>
      <Topbar
        title="OVERVIEW"
        rightSlot={
          <>
            <Chip tone="purple">Live</Chip>
            <Chip>{venues.length} rows</Chip>
            <Button
              variant="secondary" size="sm"
              leftIcon={<RefreshCw size={14} className={refresh.isPending ? "animate-spin" : ""} />}
              onClick={() => refresh.mutate()}
              loading={refresh.isPending}
            >
              {refresh.isPending ? "Refreshing…" : "Refresh signals"}
            </Button>
          </>
        }
      />
      <main className="flex-1 space-y-6 p-6">
        {refreshed && <Chip tone="aqua">{refreshed}</Chip>}

        <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
          {items.map(([label, value], i) => (
            <div key={label} className={cn("rounded-xl2 border bg-gradient-to-br p-4", statTones[i])}>
              <p className="text-[11px] uppercase tracking-[0.22em] text-white/60">{label}</p>
              <p className="mt-2 font-display text-4xl tracking-wider text-white">{value}</p>
            </div>
          ))}
        </div>

        <div className="grid gap-4 lg:grid-cols-2">
          <Panel title="Top scores">
            <ResponsiveContainer>
              <BarChart data={top} margin={{ top: 10, right: 10, bottom: 0, left: -20 }}>
                <CartesianGrid stroke="#1c1330" vertical={false} />
                <XAxis dataKey="name" stroke="#6f5a94" tick={{ fontSize: 10 }} interval={0} angle={-20} textAnchor="end" height={60} />
                <YAxis stroke="#6f5a94" tick={{ fontSize: 10 }} domain={[0, 10]} />
                <Tooltip contentStyle={{ background: "#11071F", border: "1px solid #2A1846", borderRadius: 10, color: "#fff" }} />
                <Bar dataKey="score" fill="#B15CFF" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Panel>
          <Panel title="Average signals">
            <ResponsiveContainer>
              <LineChart data={avgSignals} margin={{ top: 10, right: 10, bottom: 0, left: -20 }}>
                <CartesianGrid stroke="#1c1330" vertical={false} />
                <XAxis dataKey="name" stroke="#6f5a94" tick={{ fontSize: 10 }} />
                <YAxis stroke="#6f5a94" tick={{ fontSize: 10 }} domain={[0, 10]} />
                <Tooltip contentStyle={{ background: "#11071F", border: "1px solid #2A1846", borderRadius: 10, color: "#fff" }} />
                <Line type="monotone" dataKey="value" stroke="#FF2EC4" strokeWidth={3} dot={{ r: 4, fill: "#00F5FF" }} />
              </LineChart>
            </ResponsiveContainer>
          </Panel>
          <Panel title="Category mix">
            <ResponsiveContainer>
              <PieChart>
                <Pie data={byCategory} dataKey="value" nameKey="name" innerRadius={55} outerRadius={90} paddingAngle={4}>
                  {byCategory.map((_, i) => <Cell key={i} fill={PIE[i % PIE.length]} />)}
                </Pie>
                <Legend wrapperStyle={{ color: "#fff", fontSize: 11, textTransform: "uppercase", letterSpacing: "0.2em" }} />
                <Tooltip contentStyle={{ background: "#11071F", border: "1px solid #2A1846", borderRadius: 10, color: "#fff" }} />
              </PieChart>
            </ResponsiveContainer>
          </Panel>
          <Panel title="Crowd distribution">
            <ResponsiveContainer>
              <BarChart data={byCrowd} margin={{ top: 10, right: 10, bottom: 0, left: -20 }}>
                <CartesianGrid stroke="#1c1330" vertical={false} />
                <XAxis dataKey="name" stroke="#6f5a94" tick={{ fontSize: 11 }} />
                <YAxis stroke="#6f5a94" tick={{ fontSize: 11 }} allowDecimals={false} />
                <Tooltip contentStyle={{ background: "#11071F", border: "1px solid #2A1846", borderRadius: 10, color: "#fff" }} />
                <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                  {byCrowd.map((d, i) => (
                    <Cell key={i} fill={d.name === "busy" ? "#FF9A1F" : d.name === "medium" ? "#C7A7FF" : "#6B6B6B"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </Panel>
        </div>
      </main>
    </>
  );
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-xl2 border border-white/10 bg-white/[0.02] p-5">
      <p className="mb-3 text-[11px] uppercase tracking-[0.28em] text-white/55">{title}</p>
      <div className="h-64">{children}</div>
    </div>
  );
}
