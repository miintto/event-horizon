"use client";

import { useState } from "react";

import { FormActions } from "@/components/FormActions";
import { ErrorBox } from "@/components/PageShell";
import { NETWORK_DRIVER, NETWORK_NAME_MAX } from "@/lib/types";

interface NetworkFormProps {
  onSubmit: (name: string) => Promise<void>;
  onCancel: () => void;
}

export function NetworkForm({ onSubmit, onCancel }: NetworkFormProps) {
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      await onSubmit(name.trim());
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
      <Field label="Name" hint="Docker network name">
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
          maxLength={NETWORK_NAME_MAX}
          placeholder="postgres-net"
          autoCapitalize="off"
          autoCorrect="off"
          spellCheck={false}
          className={`${INPUT} font-mono`}
        />
      </Field>

      {/* overlay 는 swarm 을, macvlan 은 이 폼이 보내지 않는 options 를 요구한다 */}
      <Field label="Driver" hint="fixed — host-local bridge">
        <input
          value={NETWORK_DRIVER}
          disabled
          className={`${INPUT} font-mono disabled:text-neutral-500`}
        />
      </Field>

      <p className="text-[11px] text-neutral-600">
        Group networks by provider — postgres-net, redis-net. Adding a consumer
        is then one membership row, and the provider stays put.
      </p>

      {error && (
        <ErrorBox>
          <p className="whitespace-pre-line">{error}</p>
        </ErrorBox>
      )}

      <FormActions
        submitLabel="Create network"
        busy={busy}
        onCancel={onCancel}
      />
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
