import React from "react";
import { Link, NavLink } from "react-router-dom";
import { Menu, UserRound, Sparkles, LayoutDashboard } from "lucide-react";
import { cx } from "@/lib/cx";
import { Logo, LogoMark } from "./Logo";
import { IconButton } from "./Button";

export function Navbar({ onMenu, onAccount, rightSlot, className }) {
  return (
    <header
      className={cx(
        "sticky top-0 z-30 border-b border-white/5 bg-background-deep/70 backdrop-blur-xl",
        className
      )}
    >
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-3 px-4 py-3 md:py-4">
        <div className="flex items-center gap-3">
          <IconButton onClick={onMenu} data-testid="nav-menu" aria-label="Menu">
            <Menu size={18} />
          </IconButton>
          <Link to="/" className="flex items-center gap-2">
            <LogoMark size={26} />
            <Logo size="sm" />
          </Link>
        </div>

        <nav className="hidden items-center gap-1 md:flex">
          <NavItem to="/" end icon={<Sparkles size={14} />}>Tonight</NavItem>
          <NavItem to="/admin" icon={<LayoutDashboard size={14} />}>Admin</NavItem>
        </nav>

        <div className="flex items-center gap-2">
          {rightSlot}
          <IconButton onClick={onAccount} aria-label="Account" data-testid="nav-account">
            <UserRound size={18} />
          </IconButton>
        </div>
      </div>
    </header>
  );
}

function NavItem({ to, end, icon, children }) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        cx(
          "flex items-center gap-1.5 rounded-full px-3.5 py-1.5 text-sm transition",
          isActive
            ? "bg-primary/20 text-white border border-primary-glow/50 shadow-[0_0_16px_-4px_rgba(177,92,255,0.8)]"
            : "text-white/65 hover:text-white hover:bg-white/5 border border-transparent"
        )
      }
    >
      {icon}
      {children}
    </NavLink>
  );
}

/** Bottom tab-bar for mobile. */
export function BottomTabs({ items, activeKey, onChange }) {
  return (
    <nav
      className="fixed inset-x-0 bottom-0 z-30 mx-auto max-w-md border-t border-white/10 bg-background-deep/90 backdrop-blur-xl md:hidden"
      data-testid="bottom-tabs"
    >
      <ul className="grid grid-cols-3">
        {items.map((it) => {
          const active = it.key === activeKey;
          return (
            <li key={it.key}>
              <button
                onClick={() => onChange?.(it.key)}
                data-testid={`bottom-tab-${it.key}`}
                className={cx(
                  "flex w-full flex-col items-center gap-0.5 py-2.5 text-[11px] uppercase tracking-[0.22em]",
                  active ? "text-white" : "text-white/50"
                )}
              >
                <span
                  className={cx(
                    "rounded-full p-2 transition",
                    active ? "bg-primary/25 text-white shadow-neonPurple" : ""
                  )}
                >
                  {it.icon}
                </span>
                {it.label}
              </button>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}

export function Footer() {
  return (
    <footer className="mt-20 border-t border-white/5 bg-background-deep/60 py-8 text-center text-xs text-white/40">
      <div className="mx-auto flex max-w-6xl flex-col items-center gap-2 px-4 md:flex-row md:justify-between">
        <div className="flex items-center gap-2">
          <LogoMark size={18} />
          <span className="uppercase tracking-[0.3em]">Vibe2Nite · v1</span>
        </div>
        <span className="uppercase tracking-[0.3em]">
          Don't guess where to go. <span className="text-primary-glow">Know.</span>
        </span>
      </div>
    </footer>
  );
}
