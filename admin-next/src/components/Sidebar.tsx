"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Database, Sliders, LogOut, Coins, Rocket, Settings as SettingsIcon } from "lucide-react";
import { cn } from "@/lib/cn";
import { Logo, LogoMark } from "./Logo";

interface Props {
  onLogout: () => void;
}

const ITEMS = [
  { href: "/admin/overview", label: "Overview", icon: <LayoutDashboard size={16} /> },
  { href: "/admin/venues",   label: "Venues",   icon: <Database size={16} /> },
  { href: "/admin/signals",  label: "Signals",  icon: <Sliders size={16} /> },
  { href: "/admin/credits",  label: "Credits",  icon: <Coins size={16} /> },
  { href: "/admin/launch",   label: "Launch",   icon: <Rocket size={16} /> },
  { href: "/admin/settings", label: "Settings", icon: <SettingsIcon size={16} /> },
];

export function Sidebar({ onLogout }: Props) {
  const pathname = usePathname();
  return (
    <aside className="hidden w-64 shrink-0 flex-col border-r border-white/5 bg-background-deep/80 p-5 md:flex">
      <div className="mb-8 flex items-center gap-2">
        <LogoMark size={26} />
        <Logo size="sm" />
      </div>
      <nav className="flex flex-col gap-1">
        {ITEMS.map((it) => {
          const active = pathname?.startsWith(it.href);
          return (
            <Link
              key={it.href}
              href={it.href}
              className={cn(
                "flex items-center gap-2.5 rounded-xl px-3 py-2 text-sm transition",
                active
                  ? "bg-primary/20 text-white border border-primary-glow/50 shadow-[0_0_16px_-4px_rgba(177,92,255,0.8)]"
                  : "text-white/60 hover:bg-white/5 hover:text-white border border-transparent"
              )}
            >
              {it.icon}
              <span>{it.label}</span>
            </Link>
          );
        })}
      </nav>
      <div className="mt-auto border-t border-white/5 pt-4">
        <button
          onClick={onLogout}
          className="inline-flex items-center gap-2 rounded-full px-3 py-2 text-xs uppercase tracking-[0.22em] text-white/60 hover:text-white hover:bg-white/5"
        >
          <LogOut size={14} /> Log out
        </button>
      </div>
    </aside>
  );
}

export function Topbar({ title, rightSlot }: { title: string; rightSlot?: React.ReactNode }) {
  return (
    <header className="sticky top-0 z-20 flex items-center justify-between border-b border-white/5 bg-background-deep/80 px-6 py-4 backdrop-blur-xl">
      <div>
        <p className="text-[11px] uppercase tracking-[0.3em] text-primary-glow">Admin</p>
        <h1 className="font-display text-3xl tracking-widest text-white">{title}</h1>
      </div>
      <div className="flex items-center gap-3">{rightSlot}</div>
    </header>
  );
}
