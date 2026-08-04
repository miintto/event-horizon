"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";

export interface EntityOption {
  id: number;
  label: string;
}

interface EntitySelectProps {
  paramKey: string;
  value: number | null;
  options: EntityOption[];
  emptyLabel: string;
}

export function EntitySelect({
  paramKey,
  value,
  options,
  emptyLabel,
}: EntitySelectProps) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  function select(next: string) {
    const params = new URLSearchParams(searchParams.toString());
    params.set(paramKey, next);
    router.replace(`${pathname}?${params.toString()}`, { scroll: false });
  }

  if (options.length === 0) {
    return (
      <span className="rounded-md border border-neutral-800 bg-neutral-900 px-2.5 py-1.5 text-sm text-neutral-500">
        {emptyLabel}
      </span>
    );
  }

  return (
    <select
      value={value ?? ""}
      onChange={(e) => select(e.target.value)}
      className="max-w-full cursor-pointer rounded-md border border-neutral-700 bg-neutral-900 px-2.5 py-1.5 text-sm font-medium text-neutral-200"
    >
      {options.map((o) => (
        <option key={o.id} value={o.id}>
          {o.label}
        </option>
      ))}
    </select>
  );
}
