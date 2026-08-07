"use client";

export function FormActions({
  submitLabel,
  busyLabel = "Saving…",
  busy,
  onCancel,
}: {
  submitLabel: string;
  busyLabel?: string;
  busy: boolean;
  onCancel: () => void;
}) {
  return (
    <div className="flex items-center justify-end gap-2">
      <button
        type="button"
        onClick={onCancel}
        className="cursor-pointer rounded-md px-3 py-2 text-sm font-medium text-neutral-400 hover:bg-neutral-800 hover:text-neutral-200"
      >
        Cancel
      </button>
      <button
        type="submit"
        disabled={busy}
        className="cursor-pointer rounded-md bg-accent/80 px-3 py-2 text-sm font-medium text-white hover:bg-accent/95 disabled:opacity-60"
      >
        {busy ? busyLabel : submitLabel}
      </button>
    </div>
  );
}
