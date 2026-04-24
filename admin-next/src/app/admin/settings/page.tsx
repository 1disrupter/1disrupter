"use client";
import { useState, lazy, Suspense } from "react";
import { Palette } from "lucide-react";
import { Topbar } from "@/components/Sidebar";
import { Chip } from "@/components/ui";
import { cn } from "@/lib/cn";

// Lazy-load the Brand Kit body so it doesn't pull Recharts-less heavy
// markup into the initial Admin bundle.
const BrandKitEmbed = lazy(() => import("@/components/BrandKitEmbed"));

const SUBS = [
  { key: "brand", label: "Brand Kit", icon: <Palette size={14} /> },
] as const;

export default function SettingsPage() {
  const [sub, setSub] = useState<(typeof SUBS)[number]["key"]>("brand");

  return (
    <>
      <Topbar
        title="SETTINGS"
        rightSlot={<Chip tone="purple">admin-only</Chip>}
      />
      <main className="flex-1 space-y-5 p-6" data-testid="next-admin-settings">
        <div className="flex flex-wrap gap-2">
          {SUBS.map((s) => (
            <button
              key={s.key}
              onClick={() => setSub(s.key)}
              data-testid={`next-settings-sub-${s.key}`}
              className={cn(
                "inline-flex items-center gap-2 rounded-full border px-4 py-2 text-xs uppercase tracking-[0.22em] transition",
                sub === s.key
                  ? "border-primary-glow/60 bg-primary/15 text-white"
                  : "border-white/10 text-white/55 hover:text-white hover:bg-white/5"
              )}
            >
              {s.icon}
              {s.label}
            </button>
          ))}
        </div>

        {sub === "brand" && (
          <div
            className="rounded-2xl border border-white/10 bg-background-deep/50 overflow-hidden"
            data-testid="next-admin-brandkit"
          >
            <Suspense
              fallback={
                <div className="p-10 text-center text-xs uppercase tracking-[0.28em] text-white/50">
                  Loading brand kit…
                </div>
              }
            >
              <BrandKitEmbed />
            </Suspense>
          </div>
        )}
      </main>
    </>
  );
}
