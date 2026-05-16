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
            className="absolute left-0 top-0 h-full w-64 bg-background-deep shadow-xl p-4"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              onClick={() => setMenuOpen(false)}
              className="mb-4 text-white"
            >
              Close
            </button>

            <nav className="flex flex-col gap-4 text-white">
              <a href="/">Tonight</a>
              <a href="/admin">Admin</a>
              <a href="/owner">Owner</a>
            </nav>
          </div>
        </div>
      )}

      <main>{children}</main>
    </>
  );
}
