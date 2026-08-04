"use client";

import { formatCores, MIB } from "@/lib/format";
import type { WorkloadRevision } from "@/lib/types";

export function RevisionDetail({ revision }: { revision: WorkloadRevision }) {
  return (
    <section className="mt-8">
      <h2 className="mb-3 text-xs font-medium tracking-wide text-neutral-500 uppercase">
        Definition — rev {revision.revision}
      </h2>
      <dl className="mb-3 grid gap-x-6 gap-y-2 rounded-lg border border-neutral-800 bg-neutral-900 p-4 sm:grid-cols-3">
        <Detail label="Image" value={revision.image} />
        <Detail
          label="CPU"
          value={
            revision.cpu_limit
              ? `${formatCores(revision.cpu_limit)} cores`
              : "—"
          }
        />
        <Detail
          label="Memory"
          value={
            revision.memory_limit ? `${revision.memory_limit / MIB} MiB` : "—"
          }
        />
      </dl>
      <pre className="overflow-x-auto rounded-lg border border-neutral-800 bg-neutral-950 p-4 font-mono text-xs text-neutral-300">
        {JSON.stringify(revision.spec, null, 2)}
      </pre>
    </section>
  );
}

function Detail({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-0">
      <dt className="text-xs text-neutral-500">{label}</dt>
      <dd className="truncate text-sm text-neutral-100">{value}</dd>
    </div>
  );
}
