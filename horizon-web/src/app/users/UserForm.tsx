"use client";

import { useState } from "react";

import { FormActions } from "@/components/FormActions";
import { ErrorBox } from "@/components/PageShell";
import {
  USER_NAME_MAX,
  USER_PASSWORD_MAX,
  USER_PASSWORD_MIN,
} from "@/lib/types";
import type { UserRole } from "@/lib/types";

export interface UserFormInput {
  name?: string;
  email: string;
  password: string;
  passwordCheck: string;
  role: UserRole;
}

interface UserFormProps {
  onSubmit: (input: UserFormInput) => Promise<void>;
  onCancel: () => void;
}

export function UserForm({ onSubmit, onCancel }: UserFormProps) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordCheck, setPasswordCheck] = useState("");
  const [role, setRole] = useState<UserRole>("member");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const mismatch = passwordCheck.length > 0 && password !== passwordCheck;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (password !== passwordCheck) {
      setError("Passwords do not match.");
      return;
    }

    setError(null);
    setBusy(true);
    try {
      await onSubmit({
        name: name.trim() || undefined,
        email: email.trim(),
        password,
        passwordCheck,
        role,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create user.");
      setBusy(false);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="mb-4 flex flex-col gap-4 rounded-lg border border-neutral-800 bg-neutral-900 p-4"
    >
      <Field label="Email">
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          autoComplete="off"
          placeholder="user@example.com"
          className={INPUT}
        />
      </Field>

      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="Name" hint="Optional">
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            maxLength={USER_NAME_MAX}
            className={INPUT}
          />
        </Field>
        <Field label="Role">
          <select
            value={role}
            onChange={(e) => setRole(e.target.value as UserRole)}
            className={INPUT}
          >
            <option value="member">member</option>
            <option value="admin">admin</option>
          </select>
        </Field>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <Field
          label="Password"
          hint={`${USER_PASSWORD_MIN}-${USER_PASSWORD_MAX} chars`}
        >
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="new-password"
            minLength={USER_PASSWORD_MIN}
            maxLength={USER_PASSWORD_MAX}
            className={INPUT}
          />
        </Field>
        <Field
          label="Password Confirm"
          hint={mismatch ? "Does not match" : undefined}
        >
          <input
            type="password"
            value={passwordCheck}
            onChange={(e) => setPasswordCheck(e.target.value)}
            required
            autoComplete="new-password"
            maxLength={USER_PASSWORD_MAX}
            className={`${INPUT} ${mismatch ? "border-red-900" : ""}`}
          />
        </Field>
      </div>

      {error && (
        <ErrorBox>
          <p className="whitespace-pre-line">{error}</p>
        </ErrorBox>
      )}

      <FormActions
        submitLabel="Create user"
        busyLabel="Creating…"
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
