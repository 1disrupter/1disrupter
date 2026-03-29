import { Link, useLocation } from "react-router-dom";
import { BarChart3, Trophy, Radio, User } from "lucide-react";

const items = [
  { path: "/dashboard", label: "Dashboard", icon: BarChart3 },
  { path: "/leaderboard", label: "Leaderboard", icon: Trophy },
  { path: "/alerts", label: "Alerts", icon: Radio },
  { path: "/settings", label: "Settings", icon: User },
];

const MobileBottomNav = () => {
  const location = useLocation();

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-[#0A0A0A]/95 backdrop-blur-xl border-t border-zinc-800/50 safe-area-bottom" data-testid="mobile-bottom-nav">
      <div className="flex items-center justify-around h-14">
        {items.map((item) => {
          const active = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex flex-col items-center gap-0.5 px-3 py-1.5 rounded-xl transition-colors ${
                active ? "text-[#7B61FF]" : "text-zinc-500"
              }`}
              data-testid={`mobile-nav-${item.label.toLowerCase()}`}
            >
              <item.icon className={`w-5 h-5 ${active ? "text-[#7B61FF]" : ""}`} />
              <span className="text-[9px] font-medium">{item.label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
};

export default MobileBottomNav;
