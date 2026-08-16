"use client";

import { formatDateTime } from "@/lib/format";
import type { User, UserRole } from "@/lib/types";

export function UserList({ users }: { users: User[] }) {
  return (
    <ul className="divide-y divide-neutral-800 overflow-hidden rounded-lg border border-neutral-800 bg-neutral-900">
      {users.map((user) => (
        <li
          key={user.id}
          className="flex items-center justify-between gap-3 px-4 py-3"
        >
          <div className="min-w-0">
            <p className="truncate text-base font-medium text-neutral-100">
              {user.email}
            </p>
            <Meta user={user} />
          </div>
          <RoleChip role={user.role} />
        </li>
      ))}
    </ul>
  );
}

function Meta({ user }: { user: User }) {
  const { name, created_at } = user;
  if (!name && !created_at) return null;

  return (
    <p className="truncate text-xs text-neutral-500">
      {name && <span className="text-sm">{name}</span>}
      {name && created_at && " · "}
      {created_at && (
        <span title={new Date(created_at).toLocaleString()}>
          Joined at {formatDateTime(created_at)}
        </span>
      )}
    </p>
  );
}

function RoleChip({ role }: { role: UserRole }) {
  return (
    <span
      className={`shrink-0 rounded px-1.5 py-0.5 text-sm ${
        role === "admin"
          ? "bg-accent/15 text-accent"
          : "bg-neutral-800 text-neutral-400"
      }`}
    >
      {role}
    </span>
  );
}
