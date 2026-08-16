"use client";

import { useEffect, useState } from "react";

import { SyncBadge } from "@/components/Badges";
import { TrashIcon } from "@/components/Icons";
import { ErrorBox } from "@/components/PageShell";
import {
  attachWorkload,
  detachWorkload,
  getNetworkState,
  getNetworkWorkloads,
} from "@/lib/api";
import { formatDateTime, formatRelative } from "@/lib/format";
import type { Host, Network, NetworkHostState, Workload } from "@/lib/types";

interface NetworkDetailProps {
  network: Network;
  workloads: Workload[];
  hosts: Host[];
}

export function NetworkDetail({
  network,
  workloads,
  hosts,
}: NetworkDetailProps) {
  const [members, setMembers] = useState<Workload[]>([]);
  const [states, setStates] = useState<NetworkHostState[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reload, setReload] = useState(0);

  useEffect(() => {
    const id = network.id;
    let active = true;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const [workloadList, state] = await Promise.all([
          getNetworkWorkloads(id),
          getNetworkState(id),
        ]);
        if (active) {
          setMembers(workloadList);
          setStates(state.states);
        }
      } catch (e) {
        if (active) {
          setMembers([]);
          setStates([]);
          setError(e instanceof Error ? e.message : "Cannot load network.");
        }
      } finally {
        if (active) setLoading(false);
      }
    }

    void load();

    return () => {
      active = false;
    };
  }, [network.id, reload]);

  function refresh() {
    setReload((v) => v + 1);
  }

  async function handleAttach(workloadId: number) {
    await attachWorkload(network.id, { workload_id: workloadId });
    refresh();
  }

  async function handleDetach(workload: Workload) {
    if (!window.confirm(`Detach '${workload.name}' from '${network.name}'?`))
      return;
    try {
      await detachWorkload(network.id, workload.id);
      refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to detach.");
    }
  }

  const memberIds = new Set(members.map((m) => m.id));
  const candidates = workloads.filter((w) => !memberIds.has(w.id));

  return (
    <div className="mt-6 flex flex-col gap-6">
      {error && (
        <ErrorBox>
          <p className="whitespace-pre-line">{error}</p>
        </ErrorBox>
      )}

      <section>
        <SectionTitle count={members.length}>Members</SectionTitle>

        {loading ? (
          <p className="text-sm text-neutral-500">Loading…</p>
        ) : members.length === 0 ? (
          <p className="text-sm text-neutral-400">
            No workload is attached. Nothing on this network can reach anything
            else.
          </p>
        ) : (
          <ul className="divide-y divide-neutral-800 overflow-hidden rounded-lg border border-neutral-800 bg-neutral-900">
            {members.map((workload) => (
              <li
                key={workload.id}
                className="flex items-center justify-between gap-3 px-4 py-3"
              >
                <p className="truncate font-mono text-sm text-neutral-100">
                  {workload.name}
                </p>
                <button
                  type="button"
                  onClick={() => void handleDetach(workload)}
                  aria-label="Detach"
                  title="Detach"
                  className="shrink-0 cursor-pointer rounded-md p-1.5 text-neutral-600 hover:bg-red-950/40 hover:text-red-400"
                >
                  <TrashIcon />
                </button>
              </li>
            ))}
          </ul>
        )}

        <AttachForm candidates={candidates} onAttach={handleAttach} />
      </section>

      <section>
        <SectionTitle count={states.length}>Applied state</SectionTitle>
        <p className="mb-3 text-xs text-neutral-600">
          What each agent last reported. Changes land within one poll interval,
          and failures retry on their own — no action needed.
        </p>

        {loading ? (
          <p className="text-sm text-neutral-500">Loading…</p>
        ) : states.length === 0 ? (
          <p className="text-sm text-neutral-400">
            No host has reported yet. A host reports once it has a container to
            attach.
          </p>
        ) : (
          <ul className="divide-y divide-neutral-800 overflow-hidden rounded-lg border border-neutral-800 bg-neutral-900">
            {states.map((state) => (
              <li key={state.id} className="px-4 py-3">
                <div className="flex items-center justify-between gap-3">
                  <p className="truncate text-sm text-neutral-100">
                    {hostname(hosts, state.host_id)}
                  </p>
                  <div className="flex shrink-0 items-center gap-3">
                    <SyncBadge status={state.status} />
                    {state.synced_at && (
                      <span
                        title={formatDateTime(state.synced_at)}
                        className="text-xs text-neutral-500"
                      >
                        {formatRelative(state.synced_at)}
                      </span>
                    )}
                  </div>
                </div>
                {state.error_message && (
                  <p className="mt-1.5 font-mono text-xs break-all text-red-400">
                    {state.error_message}
                  </p>
                )}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

function AttachForm({
  candidates,
  onAttach,
}: {
  candidates: Workload[];
  onAttach: (workloadId: number) => Promise<void>;
}) {
  const [workloadId, setWorkloadId] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!workloadId) return;
    setError(null);
    setBusy(true);
    try {
      await onAttach(Number(workloadId));
      setWorkloadId("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to attach.");
    } finally {
      setBusy(false);
    }
  }

  if (candidates.length === 0) {
    return (
      <p className="mt-3 text-xs text-neutral-600">
        Every workload is already attached.
      </p>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="mt-3 flex flex-col gap-2">
      <div className="flex flex-wrap items-center gap-2">
        <select
          value={workloadId}
          onChange={(e) => setWorkloadId(e.target.value)}
          required
          className="cursor-pointer rounded-md border border-neutral-700 bg-neutral-900 px-2.5 py-1.5 text-sm text-neutral-200"
        >
          <option value="">Select workload…</option>
          {candidates.map((w) => (
            <option key={w.id} value={w.id}>
              {w.name}
            </option>
          ))}
        </select>
        <button
          type="submit"
          disabled={busy}
          className="cursor-pointer rounded-md px-2.5 py-1.5 text-sm font-medium text-neutral-400 hover:bg-neutral-800 hover:text-neutral-200 disabled:opacity-50"
        >
          {busy ? "Attaching…" : "Attach"}
        </button>
      </div>

      <p className="text-[11px] text-neutral-600">
        Other members reach this workload by its name. Container names change
        every deploy — the workload name does not.
      </p>

      {error && (
        <ErrorBox>
          <p className="whitespace-pre-line">{error}</p>
        </ErrorBox>
      )}
    </form>
  );
}

function SectionTitle({
  count,
  children,
}: {
  count: number;
  children: React.ReactNode;
}) {
  return (
    <h2 className="mb-3 text-xs font-medium tracking-wide text-neutral-500 uppercase">
      {children} {count > 0 && `(${count})`}
    </h2>
  );
}

function hostname(hosts: Host[], hostId: number): string {
  return hosts.find((h) => h.id === hostId)?.hostname ?? `host ${hostId}`;
}
