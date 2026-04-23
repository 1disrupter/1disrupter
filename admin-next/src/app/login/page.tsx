"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { LogIn, Lock } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { Button, Input } from "@/components/ui";
import { Logo, LogoMark } from "@/components/Logo";

export default function LoginPage() {
  const { login, session, ready } = useAuth();
  const router = useRouter();
  const [user, setUser] = useState("");
  const [pass, setPass] = useState("");
  const [err, setErr] = useState("");

  useEffect(() => {
    if (ready && session) router.replace("/admin/overview");
  }, [ready, session, router]);

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (login(user, pass)) router.replace("/admin/overview");
    else setErr("Invalid credentials");
  };

  return (
    <main className="flex min-h-screen items-center justify-center p-6">
      <form
        onSubmit={submit}
        className="w-full max-w-md rounded-xl3 border border-primary-glow/30 bg-background-dark/95 p-8 shadow-softPurple"
      >
        <div className="mb-6 flex flex-col items-center gap-3 text-center">
          <LogoMark size={56} />
          <Logo size="md" />
          <p className="text-[11px] uppercase tracking-[0.3em] text-white/55">Admin Console</p>
        </div>
        <div className="space-y-4">
          <Input
            label="Username"
            value={user}
            onChange={(e) => setUser(e.target.value)}
            placeholder="vibe2nite"
            autoFocus
          />
          <Input
            label="Password"
            type="password"
            value={pass}
            onChange={(e) => setPass(e.target.value)}
            placeholder="••••••••"
            error={err || undefined}
          />
          <Button variant="primary" size="lg" className="w-full" type="submit" leftIcon={<LogIn size={14} />}>
            Enter the Vibe
          </Button>
          <p className="text-center text-[11px] text-white/40">
            Demo creds — <code className="text-primary-glow">vibe2nite</code> / <code className="text-primary-glow">nightowl</code>
          </p>
          <p className="flex items-center justify-center gap-1.5 text-center text-[10px] uppercase tracking-[0.28em] text-white/35">
            <Lock size={10} /> Client-side auth — replace before prod
          </p>
        </div>
      </form>
    </main>
  );
}
