"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

import { getCurrentUser } from "@/lib/auth";

export default function LandingPage() {
  const router = useRouter();
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    getCurrentUser()
      .then((user) => {
        if (user) {
          router.replace("/board");
        } else {
          setChecking(false);
        }
      })
      .catch(() => setChecking(false));
  }, [router]);

  if (checking) {
    return null;
  }

  return (
    <div className="flex min-h-screen flex-col">
      <header className="border-b border-[var(--stroke)] bg-[var(--surface)]">
        <div className="mx-auto flex h-16 max-w-5xl items-center justify-between px-6">
          <span className="font-display text-xl font-semibold text-[var(--dark-slate)]">
            Kanban Studio
          </span>
          <div className="flex items-center gap-4">
            <Link
              href="/login"
              className="rounded-lg px-4 py-2 text-sm font-medium text-[var(--gray-text)] transition hover:text-[var(--dark-slate)]"
            >
              Sign in
            </Link>
            <Link
              href="/register"
              className="rounded-lg bg-[var(--secondary-cyan)] px-4 py-2 text-sm font-semibold text-white transition hover:opacity-90"
            >
              Get started
            </Link>
          </div>
        </div>
      </header>

      <main className="flex flex-1 items-center justify-center px-6">
        <div className="max-w-2xl text-center">
          <h1 className="font-display text-5xl font-bold leading-tight text-[var(--dark-slate)]">
            Organize your work with{" "}
            <span className="text-[var(--primary-indigo)]">intelligent</span>{" "}
            kanban boards
          </h1>
          <p className="mt-6 text-lg text-[var(--gray-text)]">
            Kanban Studio combines visual task management with AI-powered
            assistance. Create boards, manage cards, and let AI help you
            organize your workflow — all in one place.
          </p>
          <div className="mt-10 flex justify-center gap-4">
            <Link
              href="/register"
              className="rounded-lg bg-[var(--secondary-cyan)] px-6 py-3 text-base font-semibold text-white transition hover:opacity-90"
            >
              Start for free
            </Link>
            <Link
              href="/login"
              className="rounded-lg border border-[var(--stroke)] bg-[var(--surface-strong)] px-6 py-3 text-base font-medium text-[var(--dark-slate)] transition hover:border-[var(--gray-text)]"
            >
              Sign in
            </Link>
          </div>
        </div>
      </main>

      <footer className="border-t border-[var(--stroke)] py-6">
        <div className="mx-auto max-w-5xl px-6 text-center text-sm text-[var(--gray-text)]">
          Built with Next.js, FastAPI, and AI
        </div>
      </footer>
    </div>
  );
}
