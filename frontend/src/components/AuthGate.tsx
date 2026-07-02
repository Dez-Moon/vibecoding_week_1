"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { getCurrentUser, type CurrentUser } from "@/lib/auth";

const CurrentUserContext = createContext<CurrentUser | null>(null);

export function useCurrentUser(): CurrentUser | null {
  return useContext(CurrentUserContext);
}

export function AuthGate({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [resolved, setResolved] = useState(false);

  useEffect(() => {
    let cancelled = false;
    getCurrentUser().then((result) => {
      if (cancelled) return;
      if (result) {
        setUser(result);
      } else {
        router.replace("/login");
      }
      setResolved(true);
    });
    return () => {
      cancelled = true;
    };
  }, [router]);

  if (!resolved || !user) {
    return null;
  }
  return (
    <CurrentUserContext.Provider value={user}>
      {children}
    </CurrentUserContext.Provider>
  );
}
