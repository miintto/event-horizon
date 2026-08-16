"use client";

import { useEffect, useState } from "react";

import {
  ErrorBox,
  NewButton,
  PageHeader,
  PageShell,
  Pagination,
} from "@/components/PageShell";
import { createUser, getUsers } from "@/lib/api";
import type { User } from "@/lib/types";

import { UserForm, type UserFormInput } from "./UserForm";
import { UserList } from "./UserList";

const PAGE_SIZE = 10;

export default function UserPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [page, setPage] = useState(1);
  const [reload, setReload] = useState(0);
  const [creating, setCreating] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const res = await getUsers({ page, size: PAGE_SIZE });
        if (active) setUsers(res.users);
      } catch (e) {
        if (active) {
          setUsers([]);
          setError(e instanceof Error ? e.message : "Cannot load users.");
        }
      } finally {
        if (active) setLoading(false);
      }
    }

    void load();

    return () => {
      active = false;
    };
  }, [page, reload]);

  async function handleCreate(input: UserFormInput) {
    await createUser(input);
    setCreating(false);
    setPage(1);
    setReload((v) => v + 1);
  }

  return (
    <PageShell>
      <PageHeader title="Users">
        {!creating && (
          <NewButton label="user" onClick={() => setCreating(true)} />
        )}
      </PageHeader>

      {creating && (
        <UserForm onSubmit={handleCreate} onCancel={() => setCreating(false)} />
      )}

      {error && (
        <ErrorBox>
          <p className="whitespace-pre-line">{error}</p>
        </ErrorBox>
      )}

      {loading ? (
        <p className="text-sm text-neutral-500">Loading…</p>
      ) : users.length === 0 ? (
        <p className="text-sm text-neutral-400">
          {page > 1 ? "No users on this page." : "No users registered."}
        </p>
      ) : (
        <UserList users={users} />
      )}

      <Pagination
        page={page}
        hasPrev={page > 1}
        hasNext={users.length === PAGE_SIZE}
        busy={loading}
        onPrev={() => setPage((p) => p - 1)}
        onNext={() => setPage((p) => p + 1)}
      />
    </PageShell>
  );
}
