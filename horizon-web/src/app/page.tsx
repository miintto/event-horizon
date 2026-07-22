"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import { listHosts } from "@/lib/api";
import type { Host } from "@/lib/types";

export default function DashboardPage() {
  const [hosts, setHosts] = useState<Host[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    listHosts()
      .then((h) => active && setHosts(h))
      .catch(
        (e) =>
          active &&
          setError(
            e instanceof Error ? e.message : "호스트를 불러오지 못했습니다",
          ),
      )
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, []);

  return (
    <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-8">
      <header className="mb-8">
        <div className="flex items-center gap-2.5">
          <LogoMark />
          <h1 className="text-2xl font-semibold text-neutral-100">
            Event Horizon
          </h1>
        </div>
        <p className="mt-1 text-sm text-neutral-400">
          A lightweight infrastructure monitoring dashboard
        </p>
      </header>

      <section>
        <h2 className="mb-3 text-sm font-medium text-neutral-400">
          Hosts {!loading && !error && `(${hosts.length})`}
        </h2>

        {loading ? (
          <p className="text-sm text-neutral-500">Loading…</p>
        ) : error ? (
          <div className="rounded-md border border-red-900/50 bg-red-950/40 p-4 text-sm text-red-300">
            <p className="font-medium">Fail to load API Server</p>
            <p className="mt-1 text-red-400/80">{error}</p>
            <p className="mt-2 text-xs text-neutral-500">
              horizon-api 실행 여부와 NEXT_PUBLIC_API_URL 환경변수를 확인하세요.
            </p>
          </div>
        ) : hosts.length === 0 ? (
          <p className="text-sm text-neutral-400">No hosts.</p>
        ) : (
          <ul className="divide-y divide-neutral-800 overflow-hidden rounded-lg border border-neutral-800 bg-neutral-900">
            {hosts.map((host) => (
              <li key={host.id}>
                <Link
                  href={`/host?host_id=${host.id}`}
                  className="flex items-center justify-between px-4 py-3 hover:bg-neutral-800/60"
                >
                  <div>
                    <p className="font-medium text-neutral-100">
                      {host.hostname}
                    </p>
                    <p className="text-xs text-neutral-500">
                      {host.agent_uuid}
                    </p>
                  </div>
                  <StatusBadge status={host.status} />
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}

function LogoMark() {
  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src="/logo.png"
      alt="Event Horizon logo"
      width={56}
      height={56}
      className="shrink-0 object-contain"
    />
  );
}

function StatusBadge({ status }: { status: Host["status"] }) {
  const online = status === "online";
  return (
    <span className="inline-flex items-center gap-1.5 text-xs font-medium">
      <span
        className={`inline-block h-2 w-2 rounded-full ${
          online ? "bg-emerald-500" : "bg-neutral-600"
        }`}
      />
      <span className={online ? "text-emerald-400" : "text-neutral-400"}>
        {status}
      </span>
    </span>
  );
}
