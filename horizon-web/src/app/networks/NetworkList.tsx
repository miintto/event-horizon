"use client";

import { TrashIcon } from "@/components/Icons";
import { formatDateTime } from "@/lib/format";
import type { Network } from "@/lib/types";

interface NetworkListProps {
  networks: Network[];
  selectedId: number | null;
  onSelect: (id: number) => void;
  onDelete: (network: Network) => void;
}

export function NetworkList({
  networks,
  selectedId,
  onSelect,
  onDelete,
}: NetworkListProps) {
  return (
    <ul className="divide-y divide-neutral-800 overflow-hidden rounded-lg border border-neutral-800 bg-neutral-900">
      {networks.map((network) => (
        <li
          key={network.id}
          className={`flex items-center gap-3 ${
            network.id === selectedId ? "bg-neutral-800/40" : ""
          }`}
        >
          <button
            type="button"
            onClick={() => onSelect(network.id)}
            className="flex min-w-0 flex-1 cursor-pointer items-center justify-between gap-3 px-4 py-3 text-left hover:bg-neutral-800/60"
          >
            <div className="min-w-0">
              <p className="truncate font-mono text-sm font-medium text-neutral-100">
                {network.name}
              </p>
              <p className="truncate text-xs text-neutral-500">
                {network.driver}
                {network.created_at &&
                  ` · Created: ${formatDateTime(network.created_at)}`}
              </p>
            </div>
          </button>
          <button
            type="button"
            onClick={() => onDelete(network)}
            aria-label="Delete"
            title="Delete"
            className="mr-2.5 shrink-0 cursor-pointer rounded-md p-1.5 text-neutral-600 hover:bg-red-950/40 hover:text-red-400"
          >
            <TrashIcon />
          </button>
        </li>
      ))}
    </ul>
  );
}
