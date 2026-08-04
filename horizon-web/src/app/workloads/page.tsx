"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import {
  ErrorBox,
  NewButton,
  PageHeader,
  PageShell,
} from "@/components/PageShell";
import { createWorkload, getWorkloads } from "@/lib/api";
import type { RevisionDefinitionInput, Workload } from "@/lib/types";

import { RevisionForm } from "./RevisionForm";
import { WorkloadList } from "./WorkloadList";

export default function WorkloadPage() {
  return (
    <Suspense fallback={<PageShell>Loading…</PageShell>}>
      <Workloads />
    </Suspense>
  );
}

function Workloads() {
  const router = useRouter();

  const [workloads, setWorkloads] = useState<Workload[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    async function load() {
      setLoading(true);
      try {
        const list = await getWorkloads();
        if (active) setWorkloads(list);
      } catch (e) {
        if (active) {
          setError(e instanceof Error ? e.message : "Cannot load workloads.");
        }
      } finally {
        if (active) setLoading(false);
      }
    }

    void load();

    return () => {
      active = false;
    };
  }, []);

  async function handleCreate(
    name: string,
    definition: RevisionDefinitionInput,
  ) {
    const created = await createWorkload(name, definition);
    setShowForm(false);
    router.push(`/workloads/revisions?workload_id=${created.id}`);
  }

  return (
    <PageShell>
      <PageHeader title="Workloads">
        {!showForm && (
          <NewButton label="workload" onClick={() => setShowForm(true)} />
        )}
      </PageHeader>

      {showForm && (
        <RevisionForm
          withName
          submitLabel="Create workload"
          onSubmit={handleCreate}
          onCancel={() => setShowForm(false)}
        />
      )}

      {error && (
        <ErrorBox>
          <p className="whitespace-pre-line">{error}</p>
        </ErrorBox>
      )}

      {loading ? (
        <p className="text-sm text-neutral-500">Loading…</p>
      ) : workloads.length === 0 ? (
        <p className="text-sm text-neutral-400">
          No workloads defined. Use New workload to create the first definition.
        </p>
      ) : (
        <WorkloadList workloads={workloads} />
      )}
    </PageShell>
  );
}
