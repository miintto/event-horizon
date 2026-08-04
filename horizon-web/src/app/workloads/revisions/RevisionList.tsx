"use client";

import { formatCores, formatDateTime, MIB } from "@/lib/format";
import type { WorkloadRevision } from "@/lib/types";

interface RevisionListProps {
  revisions: WorkloadRevision[];
  selectedId: number | null;
  /** workload 가 현재 가리키는 revision. 배지로 표시한다 */
  currentRevisionId?: number;
  onSelect: (id: number) => void;
}

export function RevisionList({
  revisions,
  selectedId,
  currentRevisionId,
  onSelect,
}: RevisionListProps) {
  return (
    <ul className="divide-y divide-neutral-800 overflow-hidden rounded-lg border border-neutral-800 bg-neutral-900">
      {revisions.map((revision) => (
        <li key={revision.id}>
          <button
            type="button"
            onClick={() => onSelect(revision.id)}
            className={`flex w-full cursor-pointer items-center justify-between gap-3 px-4 py-3 text-left hover:bg-neutral-800/60 ${
              revision.id === selectedId ? "bg-neutral-800/40" : ""
            }`}
          >
            <div className="min-w-0">
              <p className="flex items-center gap-3">
                <span className="font-medium text-neutral-100">
                  rev {revision.revision}
                </span>
                {revision.id === currentRevisionId && (
                  <span className="rounded bg-accent/15 px-1.5 text-sm font-medium text-accent">
                    current
                  </span>
                )}
              </p>
              <p className="truncate text-xs text-neutral-500">
                {revision.image}
              </p>
            </div>
            <p className="shrink-0 text-right text-xs text-neutral-500">
              {formatLimits(revision)}
              {revision.created_at && (
                <>
                  <br />
                  {formatDateTime(revision.created_at)}
                </>
              )}
            </p>
          </button>
        </li>
      ))}
    </ul>
  );
}

function formatLimits(revision: WorkloadRevision): string {
  const parts = [];
  if (revision.cpu_limit)
    parts.push(`${formatCores(revision.cpu_limit)} cores`);
  if (revision.memory_limit) parts.push(`${revision.memory_limit / MIB} MiB`);
  return parts.join(" · ") || "no limits";
}
