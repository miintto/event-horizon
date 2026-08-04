"use client";

import { useState } from "react";

import { ErrorBox } from "@/components/PageShell";
import { SECRET_NAME_MAX, SECRET_VALUE_MAX } from "@/lib/types";

interface SecretFormProps {
  name?: string;
  submitLabel: string;
  onSubmit: (name: string, value: string) => Promise<void>;
  onCancel: () => void;
}

export function SecretForm({
  name: fixedName,
  submitLabel,
  onSubmit,
  onCancel,
}: SecretFormProps) {
  const [name, setName] = useState(fixedName ?? "");
  const [value, setValue] = useState("");
  const [reveal, setReveal] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const editing = fixedName != null;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      await onSubmit(name.trim(), value);
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
      <Field
        label="Name"
        hint={
          editing
            ? "Name cannot be changed"
            : "Matches the ref used in a revision"
        }
      >
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
          disabled={editing}
          maxLength={SECRET_NAME_MAX}
          placeholder="postgres/password"
          className={`${INPUT} font-mono disabled:text-neutral-500`}
        />
      </Field>

      <Field label="Value" hint="Cannot be viewed again after saving">
        <textarea
          value={value}
          onChange={(e) => setValue(e.target.value)}
          required
          rows={3}
          spellCheck={false}
          maxLength={SECRET_VALUE_MAX}
          className={`${INPUT} resize-y font-mono text-xs ${
            reveal ? "" : "[-webkit-text-security:disc]"
          }`}
        />
      </Field>

      <label className="flex cursor-pointer items-center gap-2 text-xs text-neutral-500">
        <input
          type="checkbox"
          checked={reveal}
          onChange={(e) => setReveal(e.target.checked)}
          className="cursor-pointer accent-neutral-500"
        />
        Show value
      </label>

      {error && (
        <ErrorBox>
          <p className="whitespace-pre-line">{error}</p>
        </ErrorBox>
      )}

      <div className="flex items-center gap-2">
        <button
          type="submit"
          disabled={busy}
          className="cursor-pointer rounded-md bg-accent/80 px-3 py-2 text-sm font-medium text-white hover:bg-accent/95 disabled:opacity-60"
        >
          {busy ? "Saving…" : submitLabel}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="cursor-pointer rounded-md px-3 py-2 text-sm font-medium text-neutral-400 hover:bg-neutral-800 hover:text-neutral-200"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}

const INPUT =
  "w-full rounded-md border border-neutral-700 bg-neutral-950 px-3 py-2 text-sm text-neutral-100 outline-none focus:border-neutral-500";

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
