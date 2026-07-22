"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";

import {
  finestIntervalFor,
  INTERVAL_OPTIONS,
  isComboAllowed,
  RANGE_OPTIONS,
  type RangeKey,
} from "@/lib/metrics";
import type { AggregateInterval } from "@/lib/types";

interface RangeControlsProps {
  interval: AggregateInterval;
  range: RangeKey;
  busy: boolean;
  onRefresh: () => void;
}

export function RangeControls({
  interval,
  range,
  busy,
  onRefresh,
}: RangeControlsProps) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  function apply(nextInterval: AggregateInterval, nextRange: RangeKey) {
    const params = new URLSearchParams(searchParams.toString());
    params.set("interval", nextInterval);
    params.set("range", nextRange);
    router.replace(`${pathname}?${params.toString()}`, { scroll: false });
  }

  function selectRange(next: RangeKey) {
    const nextInterval = isComboAllowed(interval, next)
      ? interval
      : finestIntervalFor(next);
    apply(nextInterval, next);
  }

  function selectInterval(next: AggregateInterval) {
    apply(next, range);
  }

  return (
    <div className="flex flex-wrap items-center gap-x-2">
      <div className="flex items-center gap-2">
        <select
          value={range}
          onChange={(e) => selectRange(e.target.value as RangeKey)}
          className="cursor-pointer rounded-md border border-neutral-700 bg-neutral-900 px-2.5 py-1.5 text-sm font-medium text-neutral-200"
        >
          {RANGE_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
      </div>

      <div className="flex items-center gap-2">
        <select
          value={interval}
          onChange={(e) => selectInterval(e.target.value as AggregateInterval)}
          className="cursor-pointer rounded-md border border-neutral-700 bg-neutral-900 px-2.5 py-1.5 text-sm font-medium text-neutral-200"
        >
          {INTERVAL_OPTIONS.map((o) => (
            <option
              key={o.value}
              value={o.value}
              disabled={!isComboAllowed(o.value, range)}
            >
              {o.label}
            </option>
          ))}
        </select>
      </div>

      <button
        type="button"
        onClick={onRefresh}
        disabled={busy}
        className="ml-auto inline-flex cursor-pointer items-center gap-1.5 rounded-md bg-neutral-900 p-2 text-neutral-400 hover:bg-neutral-800 disabled:opacity-60"
      >
        <RefreshIcon spinning={busy} />
      </button>
    </div>
  );
}

function RefreshIcon({ spinning }: { spinning: boolean }) {
  return (
    <svg
      className={spinning ? "animate-spin" : ""}
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M21 12a9 9 0 1 1-2.64-6.36" />
      <path d="M21 3v6h-6" />
    </svg>
  );
}
