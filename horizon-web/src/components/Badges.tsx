import type {
  Container,
  DeploymentStatus,
  Host,
  NetworkSyncStatus,
} from "@/lib/types";

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

const DEPLOYMENT_COLORS: Record<DeploymentStatus, string> = {
  succeeded: "bg-emerald-500 text-emerald-400",
  running: "bg-amber-500 text-amber-400",
  pending: "bg-amber-500 text-amber-400",
  failed: "bg-red-500 text-red-400",
};

export function DeploymentBadge({ status }: { status: DeploymentStatus }) {
  const [dot, text] = DEPLOYMENT_COLORS[status].split(" ");
  return (
    <span className="inline-flex shrink-0 items-center gap-1.5 text-xs font-medium">
      <span className={`inline-block h-2 w-2 rounded-full ${dot}`} />
      <span className={text}>{status}</span>
    </span>
  );
}

export function SyncBadge({ status }: { status: NetworkSyncStatus }) {
  const synced = status === "SYNCED";
  return (
    <span className="inline-flex shrink-0 items-center gap-1.5 text-xs font-medium">
      <span
        className={`inline-block h-2 w-2 rounded-full ${
          synced ? "bg-emerald-500" : "bg-red-500"
        }`}
      />
      <span className={synced ? "text-emerald-400" : "text-red-400"}>
        {synced ? "synced" : "failed"}
      </span>
    </span>
  );
}
