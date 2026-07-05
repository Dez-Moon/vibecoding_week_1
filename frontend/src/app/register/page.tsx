"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

import { register } from "@/lib/auth";

export default function RegisterPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await register(username, password);
      router.replace("/board");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[var(--surface-muted)] px-6">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-sm rounded-2xl border border-[var(--stroke)] bg-[var(--surface)] p-8 shadow-sm"
      >
        <h1 className="font-display text-2xl font-semibold text-[var(--dark-slate)]">
          Create account
        </h1>
        <p className="mt-2 text-sm text-[var(--gray-text)]">
          Start managing your tasks with AI-powered kanban boards.
        </p>

        <label className="mt-6 block text-sm font-medium text-[var(--dark-slate)]">
          Username
          <input
            data-testid="input-username"
            name="username"
            type="text"
            autoComplete="username"
            required
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="mt-1 block w-full rounded-lg border border-[var(--stroke)] bg-[var(--surface)] px-3 py-2 text-[var(--dark-slate)] outline-none focus:border-[var(--primary-indigo)]"
          />
        </label>

        <label className="mt-4 block text-sm font-medium text-[var(--dark-slate)]">
          Password
          <input
            data-testid="input-password"
            name="password"
            type="password"
            autoComplete="new-password"
            required
            minLength={4}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 block w-full rounded-lg border border-[var(--stroke)] bg-[var(--surface)] px-3 py-2 text-[var(--dark-slate)] outline-none focus:border-[var(--primary-indigo)]"
          />
        </label>

        {error ? (
          <p
            data-testid="error-message"
            className="mt-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700"
          >
            {error}
          </p>
        ) : null}

        <button
          data-testid="submit-register"
          type="submit"
          disabled={submitting}
          className="mt-6 block w-full rounded-lg bg-[var(--secondary-cyan)] px-4 py-2 font-semibold text-white transition hover:opacity-90 disabled:opacity-50"
        >
          {submitting ? "Creating account…" : "Create account"}
        </button>

        <p className="mt-4 text-center text-sm text-[var(--gray-text)]">
          Already have an account?{" "}
          <Link
            href="/login"
            className="font-medium text-[var(--primary-indigo)] hover:underline"
          >
            Sign in
          </Link>
        </p>
      </form>
    </div>
  );
}
