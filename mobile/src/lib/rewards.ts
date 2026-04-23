import React, { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { getUserId } from "@/lib/identity";
import { earnCredits, getWallet } from "@/lib/api";

/** One-shot toast hook for "+N credit" feedback. */
export function useCreditToast() {
  const [msg, setMsg] = useState<string | null>(null);
  useEffect(() => {
    if (!msg) return;
    const t = setTimeout(() => setMsg(null), 1800);
    return () => clearTimeout(t);
  }, [msg]);
  return { msg, show: (m: string) => setMsg(m) };
}

/** Fire-and-forget earn. Returns the new credit total or null on failure. */
export async function awardCredits(action: string): Promise<number | null> {
  try {
    const user_id = await getUserId();
    const r = await earnCredits(user_id, action);
    return r.credits;
  } catch {
    return null;
  }
}

/** Subscribe to the current wallet balance. */
export function useWallet() {
  const [uid, setUid] = useState<string | null>(null);
  useEffect(() => { getUserId().then(setUid); }, []);
  return useQuery({
    queryKey: ["wallet", uid],
    enabled: !!uid,
    queryFn: () => getWallet(uid!),
  });
}

export function useUserId() {
  const [uid, setUid] = useState<string | null>(null);
  useEffect(() => { getUserId().then(setUid); }, []);
  return uid;
}
