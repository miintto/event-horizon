"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

import {
  ErrorBox,
  NewButton,
  PageHeader,
  PageShell,
} from "@/components/PageShell";
import { createRevision, getRevisions, getWorkload } from "@/lib/api";
import type {
  RevisionDefinitionInput,
  Workload,
  WorkloadRevision,
} from "@/lib/types";

import { RevisionForm } from "../RevisionForm";
import { WorkloadTabs } from "../WorkloadTabs";
import { RevisionDetail } from "./RevisionDetail";
import { RevisionList } from "./RevisionList";

export default function WorkloadDetailsPage() {
  return (
    <Suspense fallback={<PageShell>Loading…</PageShell>}>
      <WorkloadDetails />
    </Suspense>
  );
}

function WorkloadDetails() {
  const sp = useSearchParams();
  const paramWorkloadId = Number(sp.get("workload_id"));

  const [workload, setWorkload] = useState<Workload | null>(null);
  const [revisions, setRevisions] = useState<WorkloadRevision[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  const workloadId =
    Number.isFinite(paramWorkloadId) && paramWorkloadId > 0
      ? paramWorkloadId
      : null;

  useEffect(() => {
    const id = workloadId;
    let active = true;

    async function load() {
      setWorkload(null);
      setRevisions([]);
      setSelectedId(null);
      if (id == null) {
        setLoading(false);
        return;
      }
      setLoading(true);
      try {
        const [detail, list] = await Promise.all([
          getWorkload(id),
          getRevisions(id),
        ]);
        if (active) {
          setWorkload(detail);
          setRevisions(list);
          setSelectedId(list[0]?.id ?? null);
        }
      } catch (e) {
        if (active) {
          setError(e instanceof Error ? e.message : "Cannot load revisions.");
        }
      } finally {
        if (active) setLoading(false);
      }
    }

    void load();

    return () => {
      active = false;
    };
  }, [workloadId, reloadKey]);

  const selected = revisions.find((r) => r.id === selectedId) ?? null;
  const current = revisions.find((r) => r.id === workload?.current_revision_id);

  async function handleCreate(
    _name: string,
    definition: RevisionDefinitionInput,
  ) {
    if (workloadId == null) return;
    await createRevision(workloadId, definition);
    setShowForm(false);
    setReloadKey((k) => k + 1);
  }

  return (
    <PageShell>
      <PageHeader title={workload?.name ?? "Workload"} />
      <WorkloadTabs workloadId={workloadId} />

      {error && (
        <ErrorBox>
          <p className="whitespace-pre-line">{error}</p>
        </ErrorBox>
      )}

      {workloadId == null ? (
        <p className="text-sm text-neutral-400">
          workload_id is required. Select one from the list.
        </p>
      ) : (
        <>
          <section className="mt-2">
            <div className="mb-3 flex items-center gap-3">
              <h2 className="text-xs font-medium tracking-wide text-neutral-500 uppercase">
                Revisions {revisions.length > 0 && `(${revisions.length})`}
              </h2>
              {!showForm && (
                <NewButton label="revision" onClick={() => setShowForm(true)} />
              )}
            </div>

            {showForm && (
              <RevisionForm
                base={current ?? revisions[0]}
                submitLabel="Create revision"
                onSubmit={handleCreate}
                onCancel={() => setShowForm(false)}
              />
            )}

            {loading ? (
              <p className="text-sm text-neutral-500">Loading…</p>
            ) : revisions.length === 0 ? (
              <p className="text-sm text-neutral-400">No revisions.</p>
            ) : (
              <RevisionList
                revisions={revisions}
                selectedId={selectedId}
                currentRevisionId={workload?.current_revision_id}
                onSelect={setSelectedId}
              />
            )}
          </section>

          {selected && <RevisionDetail revision={selected} />}
        </>
      )}
    </PageShell>
  );
}
