"use client";

import { useState } from "react";

import { FormActions } from "@/components/FormActions";
import { ErrorBox } from "@/components/PageShell";
import type { Host, WorkloadRevision } from "@/lib/types";

interface DeploymentFormProps {
  hosts: Host[];
  revisions: WorkloadRevision[];
  currentRevisionId?: number;
  defaultHostId: number | null;
  onSubmit: (hostId: number, revisionId: number) => Promise<void>;
  onCancel: () => void;
}

export function DeploymentForm({
  hosts,
  revisions,
  currentRevisionId,
  defaultHostId,
  onSubmit,
  onCancel,
}: DeploymentFormProps) {
  const [hostId, setHostId] = useState(defaultHostId ?? hosts[0]?.id ?? 0);
  const [revisionId, setRevisionId] = useState(
    currentRevisionId ?? revisions[0]?.id ?? 0,
  );
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await onSubmit(hostId, revisionId);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Cannot start deployment.");
    } finally {
      setBusy(false);
    }
  }

  if (hosts.length === 0) {
    return (
      <ErrorBox>
        No hosts are registered. An agent must report metrics at least once
        before it can receive deployments.
      </ErrorBox>
    );
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="mb-4 flex flex-col gap-4 rounded-lg border border-neutral-800 bg-neutral-900 p-4"
    >
      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="Host">
          <select
            value={hostId}
            onChange={(e) => setHostId(Number(e.target.value))}
            className={INPUT}
          >
            {hosts.map((host) => (
              <option key={host.id} value={host.id}>
                {host.hostname}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Revision">
          <select
            value={revisionId}
            onChange={(e) => setRevisionId(Number(e.target.value))}
            className={INPUT}
          >
            {revisions.map((revision) => (
              <option key={revision.id} value={revision.id}>
                rev {revision.revision}
                {revision.id === currentRevisionId ? " (current)" : ""} ·{" "}
                {revision.image}
              </option>
            ))}
          </select>
        </Field>
      </div>

      {error && (
        <ErrorBox>
          <p className="whitespace-pre-line">{error}</p>
        </ErrorBox>
      )}

      <FormActions
        submitLabel="Deploy"
        busyLabel="Starting…"
        busy={busy}
        onCancel={onCancel}
      />
    </form>
  );
}

const INPUT =
  "w-full rounded-md border border-neutral-700 bg-neutral-950 px-3 py-2 text-sm text-neutral-100 outline-none focus:border-neutral-500";

function Field({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <label className="flex flex-col gap-1.5">
      <span className="text-xs font-medium text-neutral-400">{label}</span>
      {children}
    </label>
  );
}
