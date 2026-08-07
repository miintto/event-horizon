"use client";

import Link from "next/link";

import { WorkloadBadge } from "@/components/Badges";
import type { Workload } from "@/lib/types";

export function WorkloadList({ workloads }: { workloads: Workload[] }) {
  return (
    <ul className="grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-4">
      {workloads.map((workload) => (
        <li key={workload.id}>
          <Link
            href={`/workloads/containers?workload_id=${workload.id}`}
            className="flex h-full flex-col gap-2 rounded-lg border border-neutral-800 bg-neutral-900 p-4 hover:border-neutral-700 hover:bg-neutral-800/60"
          >
            <p
              title={workload.name}
              className="truncate font-medium text-neutral-100"
            >
              {workload.name}
            </p>
            <WorkloadBadge running={workload.running_count ?? 0} />
            <p className="mt-auto truncate text-xs text-neutral-500">
              {plural(workload.running_count ?? 0, "container")}
            </p>
          </Link>
        </li>
      ))}
    </ul>
  );
}

function plural(count: number, noun: string): string {
  return `${count} ${noun}${count === 1 ? "" : "s"}`;
}
