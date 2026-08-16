"use client";

import { Suspense, useEffect, useState } from "react";

import {
  ErrorBox,
  NewButton,
  PageHeader,
  PageShell,
  Pagination,
} from "@/components/PageShell";
import {
  createNetwork,
  deleteNetwork,
  getNetworks,
  getWorkloads,
  listHosts,
} from "@/lib/api";
import type { Host, Network, Workload } from "@/lib/types";
import { NETWORK_DRIVER } from "@/lib/types";

import { NetworkDetail } from "./NetworkDetail";
import { NetworkForm } from "./NetworkForm";
import { NetworkList } from "./NetworkList";

const PAGE_SIZE = 10;

export default function NetworkPage() {
  return (
    <Suspense fallback={<PageShell>Loading…</PageShell>}>
      <Networks />
    </Suspense>
  );
}

function Networks() {
  const [networks, setNetworks] = useState<Network[]>([]);
  const [workloads, setWorkloads] = useState<Workload[]>([]);
  const [hosts, setHosts] = useState<Host[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [page, setPage] = useState(1);
  const [reload, setReload] = useState(0);
  const [creating, setCreating] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const res = await getNetworks({ page, size: PAGE_SIZE });
        if (active) {
          setNetworks(res.networks);
          setSelectedId((id) =>
            res.networks.some((n) => n.id === id) ? id : null,
          );
        }
      } catch (e) {
        if (active) {
          setNetworks([]);
          setError(e instanceof Error ? e.message : "Cannot load networks.");
        }
      } finally {
        if (active) setLoading(false);
      }
    }

    void load();

    return () => {
      active = false;
    };
  }, [page, reload]);

  useEffect(() => {
    let active = true;

    async function load() {
      try {
        const [workloadList, hostList] = await Promise.all([
          getWorkloads(),
          listHosts(),
        ]);
        if (active) {
          setWorkloads(workloadList);
          setHosts(hostList);
        }
      } catch {}
    }

    void load();

    return () => {
      active = false;
    };
  }, []);

  async function handleCreate(name: string) {
    await createNetwork({ name, driver: NETWORK_DRIVER });
    setCreating(false);
    setPage(1);
    setReload((v) => v + 1);
  }

  async function handleDelete(network: Network) {
    if (
      !window.confirm(
        `Delete '${network.name}'? Members are detached, and agents drop the ` +
          `connections on their next cycle.`,
      )
    )
      return;
    try {
      await deleteNetwork(network.id);
      setReload((v) => v + 1);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Fail to remove.");
    }
  }

  const selected = networks.find((n) => n.id === selectedId) ?? null;
  const hasNext = networks.length === PAGE_SIZE;
  const hasPrev = page > 1;

  return (
    <PageShell>
      <PageHeader
        title="Networks"
        subtitle="Isolated by default — workloads only reach the networks they join."
      >
        {!creating && (
          <NewButton label="network" onClick={() => setCreating(true)} />
        )}
      </PageHeader>

      {creating && (
        <NetworkForm
          onSubmit={handleCreate}
          onCancel={() => setCreating(false)}
        />
      )}

      {error && (
        <ErrorBox>
          <p className="whitespace-pre-line">{error}</p>
        </ErrorBox>
      )}

      {loading ? (
        <p className="text-sm text-neutral-500">Loading…</p>
      ) : networks.length === 0 ? (
        <p className="text-sm text-neutral-400">
          {page > 1
            ? "No networks on this page."
            : "No networks registered. Use New network to add the first one."}
        </p>
      ) : (
        <NetworkList
          networks={networks}
          selectedId={selectedId}
          onSelect={setSelectedId}
          onDelete={(n) => void handleDelete(n)}
        />
      )}

      <Pagination
        page={page}
        hasPrev={hasPrev}
        hasNext={hasNext}
        busy={loading}
        onPrev={() => setPage((p) => p - 1)}
        onNext={() => setPage((p) => p + 1)}
      />

      {selected && (
        <NetworkDetail
          key={selected.id}
          network={selected}
          workloads={workloads}
          hosts={hosts}
        />
      )}
    </PageShell>
  );
}
