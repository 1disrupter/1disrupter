import React, { useState } from "react";

import { Locate } from "lucide-react";
import { IconButton } from "@/components/v2n/Button";


import { Navbar } from "@/components/v2n/Navbar";

export default function MainLayout({ children }) {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <>
     
<Navbar
  onMenu={() => setMenuOpen(true)}
  rightSlot={
    <IconButton
      onClick={() => window.location.reload()}
      aria-label="Use my location"
    >
      <Locate size={18} />
    </IconButton>
  }
/>

 {/* Drawer */}
      
      {menuOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50"
          onClick={() => setMenuOpen(false)}
        >
          <div
           
<div
  className="absolute left-0 top-0 h-full w-72 bg-background-deep/95 backdrop-blur-2xl border-r border-white/10 shadow-[0_0_40px_rgba(0,0,0,0.5)] p-5 animate-slideIn"




 
            onClick={(e) => e.stopPropagation()}
          >
           
<button
  onClick={() => setMenuOpen(false)}
  className="mb-5 flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-white hover:bg-white/10 transition"
>
  ✕ Close
</button>

 

<div className="mb-6 border-b border-white/10 pb-5">

  <p className="text-xs uppercase tracking-[0.3em] text-fuchsia-400 mb-2">
    Explore Tonight
  </p>

  <h2 className="text-2xl font-black text-white">
    VIBE2NITE
  </h2>

  <p className="text-white/40 text-sm mt-2">
    Live nightlife discovery.
  </p>

</div>


<nav className="flex flex-col gap-3 text-white mt-6">

  <a href="/explore"
className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white hover:bg-fuchsia-500/15 hover:border-fuchsia-400/30 hover:shadow-[0_0_20px_rgba(255,0,200,0.2)] transition-all duration-300

">
    🔥 Trending Tonight
  </a>

  <a href="/map"
className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white hover:bg-fuchsia-500/15 hover:border-fuchsia-400/30 hover:shadow-[0_0_20px_rgba(255,0,200,0.2)] transition-all duration-300"

 >
    🗺️ Live Map
  </a>

  <a href="/favourites"
className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white hover:bg-fuchsia-500/15 hover:border-fuchsia-400/30 hover:shadow-[0_0_20px_rgba(255,0,200,0.2)] transition-all duration-300"

 >
    ⭐ Favourites
  </a>

  <a href="/me"
className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white hover:bg-fuchsia-500/15 hover:border-fuchsia-400/30 hover:shadow-[0_0_20px_rgba(255,0,200,0.2)] transition-all duration-300"

 >
    👤 Profile
  </a>

  <a href="/owner"
className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white hover:bg-fuchsia-500/15 hover:border-fuchsia-400/30 hover:shadow-[0_0_20px_rgba(255,0,200,0.2)] transition-all duration-300"

 >
    🏢 Venue Owner
  </a>

  <a href="/admin"
className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white hover:bg-fuchsia-500/15 hover:border-fuchsia-400/30 hover:shadow-[0_0_20px_rgba(255,0,200,0.2)] transition-all duration-300"

 >
    ⚙️ Admin
  </a>

</nav>

           
          </div>
        </div>
      )}

      <main>{children}</main>
    </>
  );
}
