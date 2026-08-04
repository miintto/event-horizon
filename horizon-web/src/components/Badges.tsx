import type { Container, Host } from "@/lib/types";

function Dot({ on }: { on: boolean }) {
  return (
    <span
      className={`inline-block h-2 w-2 rounded-full ${
        on ? "bg-emerald-500" : "bg-neutral-600"
      }`}
    />
  );
}

function Badge({ on, children }: { on: boolean; children: React.ReactNode }) {
  return (
    <span className="inline-flex shrink-0 items-center gap-1.5 text-xs font-medium">
      <Dot on={on} />
      <span className={on ? "text-emerald-400" : "text-neutral-400"}>
        {children}
      </span>
    </span>
  );
}

export function StatusBadge({ status }: { status: Host["status"] }) {
  return <Badge on={status === "online"}>{status}</Badge>;
}

export function StateBadge({ state }: { state: Container["state"] }) {
  return <Badge on={state === "running"}>{state}</Badge>;
}

export function WorkloadBadge({ running }: { running: number }) {
  return <Badge on={running > 0}>{running > 0 ? "running" : "stopped"}</Badge>;
}
