"use client";

import { useState } from "react";

import { login } from "@/lib/api";
import { setToken } from "@/lib/auth";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const result = await login(email, password);
      setToken(result.access_token);
      window.location.href = "/";
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sign-in failed.");
      setBusy(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-4 py-12">
      <div className="w-full max-w-sm">
        <div className="mb-8 flex flex-col items-center gap-2">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/logo.png"
            alt=""
            width={48}
            height={48}
            className="object-contain"
          />
          <h1 className="text-xl font-semibold text-neutral-100">
            Event Horizon
          </h1>
        </div>

        <form onSubmit={onSubmit} className="flex flex-col gap-3">
          <label className="flex flex-col gap-1.5">
            <span className="text-xs font-medium text-neutral-400">Email</span>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="username"
              className="rounded-md border border-neutral-700 bg-neutral-900 px-3 py-3 text-sm text-neutral-100 outline-none focus:border-neutral-500"
            />
          </label>

          <label className="flex flex-col gap-1.5">
            <span className="text-xs font-medium text-neutral-400">
              Password
            </span>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
              className="rounded-md border border-neutral-700 bg-neutral-900 px-3 py-3 text-sm text-neutral-100 outline-none focus:border-neutral-500"
            />
          </label>

          {error && (
            <p className="rounded-md border border-red-900/50 bg-red-950/40 px-3 py-2 text-sm text-red-300">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={busy}
            className="mt-2 cursor-pointer rounded-md bg-accent/80 px-3 py-3 text-sm font-medium text-white hover:bg-accent/95 disabled:opacity-60"
          >
            {busy ? "Signing in…" : "Sign in"}
          </button>
        </form>
      </div>
    </main>
  );
}
