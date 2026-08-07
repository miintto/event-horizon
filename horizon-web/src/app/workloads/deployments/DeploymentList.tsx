"use client";

import { DeploymentBadge } from "@/components/Badges";
import { formatDateTime } from "@/lib/format";
import type { Deployment, Host, WorkloadRevision } from "@/lib/types";

interface DeploymentListProps {
  deployments: Deployment[];
  hosts: Host[];
  revisions: WorkloadRevision[];
}

export function DeploymentList({
  deployments,
  hosts,
  revisions,
}: DeploymentListProps) {
  const hostnames = new Map(hosts.map((h) => [h.id, h.hostname]));
  const revisionNumbers = new Map(revisions.map((r) => [r.id, r.revision]));

  return (
    <ul className="divide-y divide-neutral-800 overflow-hidden rounded-lg border border-neutral-800 bg-neutral-900">
      {deployments.map((deployment) => (
        <li key={deployment.id} className="px-4 py-3">
          <div className="flex items-center justify-between gap-3">
            <div className="flex min-w-0 items-center gap-3">
              <DeploymentBadge status={deployment.status} />
              <span className="font-medium text-neutral-100">
                rev {revisionNumbers.get(deployment.revision_id) ?? "?"}
              </span>
              <span className="truncate text-xs text-neutral-500">
                {hostnames.get(deployment.host_id) ??
                  `host ${deployment.host_id}`}
              </span>
            </div>
            <p className="shrink-0 text-right text-xs text-neutral-500">
              {deployment.created_at && formatDateTime(deployment.created_at)}
            </p>
          </div>
          {deployment.error_message && (
            <details className="group mt-2">
              <summary className="w-fit cursor-pointer list-none text-xs text-neutral-500 select-none hover:text-neutral-300">
                <span className="group-open:hidden">▸ Show error</span>
                <span className="hidden group-open:inline">▾ Hide error</span>
              </summary>
              <p className="mt-1 rounded bg-red-950/40 px-2 py-1 font-mono text-xs break-all whitespace-pre-wrap text-red-300">
                {deployment.error_message}
              </p>
            </details>
          )}
        </li>
      ))}
    </ul>
  );
}
