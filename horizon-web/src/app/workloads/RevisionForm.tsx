"use client";

import { useState } from "react";

import { FormActions } from "@/components/FormActions";
import { ErrorBox } from "@/components/PageShell";
import { formatCores, MIB } from "@/lib/format";
import type { RevisionDefinitionInput, WorkloadRevision } from "@/lib/types";

interface RevisionFormProps {
  withName?: boolean;
  base?: WorkloadRevision;
  submitLabel: string;
  onSubmit: (
    name: string,
    definition: RevisionDefinitionInput,
  ) => Promise<void>;
  onCancel: () => void;
}

export function RevisionForm({
  withName = false,
  base,
  submitLabel,
  onSubmit,
  onCancel,
}: RevisionFormProps) {
  const [name, setName] = useState("");
  const [image, setImage] = useState(base?.image ?? "");
  const [cpu, setCpu] = useState(
    base?.cpu_limit ? formatCores(base.cpu_limit) : "",
  );
  const [memoryMib, setMemoryMib] = useState(
    base?.memory_limit ? String(base.memory_limit / MIB) : "",
  );
  const [spec, setSpec] = useState(
    base?.spec ? JSON.stringify(base.spec, null, 2) : "{}",
  );
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    let parsedSpec: Record<string, unknown>;
    try {
      parsedSpec = JSON.parse(spec || "{}");
    } catch {
      setError("spec is not valid JSON");
      return;
    }

    setBusy(true);
    try {
      await onSubmit(name.trim(), {
        image: image.trim(),
        cpu_limit: cpu ? Number(cpu) : undefined,
        memory_limit: memoryMib ? Number(memoryMib) * MIB : undefined,
        spec: parsedSpec,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save.");
      setBusy(false);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="mb-4 flex flex-col gap-3 rounded-lg border border-neutral-800 bg-neutral-900 p-4"
    >
      {withName && (
        <Field label="Name">
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            placeholder="app-api-prod"
            className={INPUT}
          />
        </Field>
      )}

      <Field label="Image">
        <input
          value={image}
          onChange={(e) => setImage(e.target.value)}
          required
          placeholder="app-api:latest"
          className={INPUT}
        />
      </Field>

      <div className="grid gap-3 sm:grid-cols-2">
        <Field label="CPU (cores)" hint="Leave empty for no limit">
          <input
            type="number"
            step="0.001"
            min="0"
            value={cpu}
            onChange={(e) => setCpu(e.target.value)}
            placeholder="0.5"
            className={INPUT}
          />
        </Field>
        <Field label="Memory (MiB)" hint="At least 6 MiB">
          <input
            type="number"
            min="6"
            value={memoryMib}
            onChange={(e) => setMemoryMib(e.target.value)}
            placeholder="512"
            className={INPUT}
          />
        </Field>
      </div>

      <Field label="Spec (JSON)" hint="env · ports · mounts · healthcheck …">
        <textarea
          value={spec}
          onChange={(e) => setSpec(e.target.value)}
          rows={10}
          spellCheck={false}
          className={`${INPUT} resize-y font-mono text-xs`}
        />
      </Field>

      {error && (
        <ErrorBox>
          <p className="whitespace-pre-line">{error}</p>
        </ErrorBox>
      )}

      <FormActions submitLabel={submitLabel} busy={busy} onCancel={onCancel} />
    </form>
  );
}

const INPUT =
  "w-full rounded-md border placeholder-neutral-600 border-neutral-700 bg-neutral-950 px-3 py-2 text-sm text-neutral-100 outline-none focus:border-neutral-500";

function Field({
  label,
  hint,
  children,
}: {
  label: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <label className="flex flex-col gap-1.5">
      <span className="flex items-baseline gap-2">
        <span className="text-xs font-medium text-neutral-400">{label}</span>
        {hint && <span className="text-[11px] text-neutral-600">{hint}</span>}
      </span>
      {children}
    </label>
  );
}
