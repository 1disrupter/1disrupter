"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { Sidebar } from "@/components/Sidebar";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const { session, ready, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (ready && !session) router.replace("/login");
  }, [ready, session, router]);

  if (!ready) return null;
  if (!session) return null;

  return (
    <div className="flex min-h-screen">
      <Sidebar onLogout={() => { logout(); router.replace("/login"); }} />
      <div className="flex min-w-0 flex-1 flex-col">{children}</div>
    </div>
  );
}
