"use client";

import { PencilIcon, TrashIcon } from "@/components/Icons";
import { formatDateTime } from "@/lib/format";
import type { Secret } from "@/lib/types";

interface SecretListProps {
  secrets: Secret[];
  onEdit: (secret: Secret) => void;
  onDelete: (secret: Secret) => void;
}

export function SecretList({ secrets, onEdit, onDelete }: SecretListProps) {
  return (
    <ul className="divide-y divide-neutral-800 overflow-hidden rounded-lg border border-neutral-800 bg-neutral-900">
      {secrets.map((secret) => (
        <li
          key={secret.id}
          className="flex items-center justify-between gap-3 px-4 py-3"
        >
          <div className="min-w-0">
            <p className="truncate font-mono text-sm font-medium text-neutral-100">
              {secret.name}
            </p>
            <p className="truncate text-xs text-neutral-500">
              {secret.updated_at &&
                `Updated: ${formatDateTime(secret.updated_at)}`}
            </p>
          </div>
          <div className="flex shrink-0 items-center gap-0.5">
            <RowButton label="Update" onClick={() => onEdit(secret)}>
              <PencilIcon />
            </RowButton>
            <RowButton danger label="Delete" onClick={() => onDelete(secret)}>
              <TrashIcon />
            </RowButton>
          </div>
        </li>
      ))}
    </ul>
  );
}

function RowButton({
  danger = false,
  label,
  onClick,
  children,
}: {
  danger?: boolean;
  label: string;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-label={label}
      title={label}
      className={`cursor-pointer rounded-md p-1.5 ${
        danger
          ? "text-neutral-600 hover:bg-red-950/40 hover:text-red-400"
          : "text-neutral-600 hover:bg-neutral-800 hover:text-neutral-200"
      }`}
    >
      {children}
    </button>
  );
}
