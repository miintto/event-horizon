"use client";

import { Suspense, useEffect, useState } from "react";

import {
  ErrorBox,
  NewButton,
  PageHeader,
  PageShell,
} from "@/components/PageShell";
import {
  createSecret,
  deleteSecret,
  getSecrets,
  updateSecret,
} from "@/lib/api";
import type { Secret } from "@/lib/types";

import { SecretForm } from "./SecretForm";
import { SecretList } from "./SecretList";

const PAGE_SIZE = 10;

export default function SecretPage() {
  return (
    <Suspense fallback={<PageShell>Loading…</PageShell>}>
      <Secrets />
    </Suspense>
  );
}

function Secrets() {
  const [secrets, setSecrets] = useState<Secret[]>([]);
  const [page, setPage] = useState(1);
  const [reload, setReload] = useState(0);
  const [creating, setCreating] = useState(false);
  const [editing, setEditing] = useState<Secret | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const res = await getSecrets({ page, size: PAGE_SIZE });
        if (active) setSecrets(res.secrets);
      } catch (e) {
        if (active) {
          setSecrets([]);
          setError(e instanceof Error ? e.message : "Cannot load secrets.");
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

  function refresh() {
    setReload((v) => v + 1);
  }

  function startCreate() {
    setEditing(null);
    setCreating(true);
  }

  function startEdit(secret: Secret) {
    setCreating(false);
    setEditing(secret);
  }

  async function handleCreate(name: string, value: string) {
    await createSecret(name, value);
    setCreating(false);
    setPage(1);
    refresh();
  }

  async function handleUpdate(_name: string, value: string) {
    if (!editing) return;
    await updateSecret(editing.id, value);
    setEditing(null);
    refresh();
  }

  async function handleDelete(secret: Secret) {
    if (!window.confirm(`Delete '${secret.name}'?`)) return;
    try {
      await deleteSecret(secret.id);
      refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Fail to remove.");
    }
  }

  const hasNext = secrets.length === PAGE_SIZE;
  const hasPrev = page > 1;
  const formOpen = creating || editing != null;

  return (
    <PageShell>
      <PageHeader title="Secrets">
        {!formOpen && <NewButton label="secret" onClick={startCreate} />}
      </PageHeader>

      {creating && (
        <SecretForm
          submitLabel="Create secret"
          onSubmit={handleCreate}
          onCancel={() => setCreating(false)}
        />
      )}

      {editing && (
        <SecretForm
          name={editing.name}
          submitLabel="Replace value"
          onSubmit={handleUpdate}
          onCancel={() => setEditing(null)}
        />
      )}

      {error && (
        <ErrorBox>
          <p className="whitespace-pre-line">{error}</p>
        </ErrorBox>
      )}

      {loading ? (
        <p className="text-sm text-neutral-500">Loading…</p>
      ) : secrets.length === 0 ? (
        <p className="text-sm text-neutral-400">
          {page > 1
            ? "No secrets on this page."
            : "No secrets registered. Use New secret to add the first one."}
        </p>
      ) : (
        <SecretList
          secrets={secrets}
          onEdit={startEdit}
          onDelete={(s) => void handleDelete(s)}
        />
      )}

      {(hasPrev || hasNext) && (
        <nav className="mt-4 flex items-center justify-between gap-3">
          <PageButton
            disabled={!hasPrev || loading}
            onClick={() => setPage((p) => p - 1)}
          >
            Prev
          </PageButton>
          <span className="text-xs text-neutral-500">{page} Page</span>
          <PageButton
            disabled={!hasNext || loading}
            onClick={() => setPage((p) => p + 1)}
          >
            Next
          </PageButton>
        </nav>
      )}
    </PageShell>
  );
}

function PageButton({
  disabled,
  onClick,
  children,
}: {
  disabled: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      disabled={disabled}
      onClick={onClick}
      className="cursor-pointer rounded-md border border-neutral-800 px-3 py-1.5 text-sm font-medium text-neutral-400 hover:bg-neutral-800 hover:text-neutral-200 disabled:cursor-default disabled:opacity-40 disabled:hover:bg-transparent disabled:hover:text-neutral-400"
    >
      {children}
    </button>
  );
}
