"use client";

import Link from "next/link";

import { WorkloadBadge } from "@/components/Badges";
import { ChevronIcon } from "@/components/Icons";
import type { Workload } from "@/lib/types";

export function WorkloadList({ workloads }: { workloads: Workload[] }) {
  return (
    <ul className="divide-y divide-neutral-800 overflow-hidden rounded-lg border border-neutral-800 bg-neutral-900">
      {workloads.map((workload) => (
        <li key={workload.id}>
          <Link
            href={`/workloads/containers?workload_id=${workload.id}`}
            className="flex items-center justify-between gap-3 px-4 py-3 hover:bg-neutral-800/60"
          >
            <div className="min-w-0">
              <p className="truncate font-medium text-neutral-100">
                {workload.name}
              </p>
              <p className="truncate text-xs text-neutral-500">
                {plural(workload.running_count ?? 0, "container")}
              </p>
            </div>
            <div className="flex shrink-0 items-center gap-3">
              <WorkloadBadge running={workload.running_count ?? 0} />
              <ChevronIcon />
            </div>
          </Link>
        </li>
      ))}
    </ul>
  );
}

function plural(count: number, noun: string): string {
  return `${count} ${noun}${count === 1 ? "" : "s"}`;
}
