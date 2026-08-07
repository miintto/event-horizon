"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

import { RefreshIcon } from "@/components/Icons";
import { ErrorBox, PageHeader, PageShell } from "@/components/PageShell";
import {
  createDeployment,
  getContainers,
  getDeployments,
  getRevisions,
  getWorkload,
  listHosts,
} from "@/lib/api";
import type { Deployment, Host, Workload, WorkloadRevision } from "@/lib/types";

import { WorkloadTabs } from "../WorkloadTabs";
import { DeploymentForm } from "./DeploymentForm";
import { DeploymentList } from "./DeploymentList";

export default function DeploymentPage() {
  return (
    <Suspense fallback={<PageShell>Loading…</PageShell>}>
      <Deployments />
    </Suspense>
  );
}

function Deployments() {
  const sp = useSearchParams();
  const paramWorkloadId = Number(sp.get("workload_id"));

  const [workload, setWorkload] = useState<Workload | null>(null);
  const [deployments, setDeployments] = useState<Deployment[]>([]);
  const [hosts, setHosts] = useState<Host[]>([]);
  const [revisions, setRevisions] = useState<WorkloadRevision[]>([]);
  const [defaultHostId, setDefaultHostId] = useState<number | null>(null);
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
      if (id == null) {
        setLoading(false);
        return;
      }
      setLoading(true);
      try {
        const [detail, history, hostList, revisionList, containers] =
          await Promise.all([
            getWorkload(id),
            getDeployments({ workloadId: id }),
            listHosts(),
            getRevisions(id),
            getContainers({ workloadId: id }),
          ]);
        if (!active) return;

        setWorkload(detail);
        setDeployments(history);
        setHosts(hostList);
        setRevisions(revisionList);
        setDefaultHostId(containers[0]?.host_id ?? null);
        setError(null);
      } catch (e) {
        if (active) {
          setError(e instanceof Error ? e.message : "Cannot load deployments.");
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

  const active = deployments.find(
    (d) => d.status === "pending" || d.status === "running",
  );
  const deployDisabled =
    Boolean(active) || workload?.current_revision_id == null;
  const disabledReason = active
    ? "A deployment is already in progress"
    : "This workload has no revision to deploy";

  async function handleDeploy(hostId: number, revisionId: number) {
    if (workloadId == null) return;
    await createDeployment({ hostId, workloadId, revisionId });
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
        <section className="mt-2">
          <div className="mb-3 flex items-center gap-3">
            <h2 className="text-xs font-medium tracking-wide text-neutral-500 uppercase">
              Deployments {deployments.length > 0 && `(${deployments.length})`}
            </h2>
            <div className="ml-auto flex items-center gap-2">
              {!showForm && (
                <button
                  type="button"
                  onClick={() => setShowForm(true)}
                  disabled={deployDisabled}
                  title={deployDisabled ? disabledReason : undefined}
                  className="cursor-pointer rounded-md px-2.5 py-1 text-sm font-medium text-neutral-400 hover:bg-neutral-800 hover:text-neutral-200 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  Deploy
                </button>
              )}
              <button
                type="button"
                onClick={() => setReloadKey((k) => k + 1)}
                disabled={loading}
                aria-label="Refresh deployments"
                className="inline-flex cursor-pointer items-center gap-1.5 rounded-md bg-neutral-900 p-2 text-neutral-400 hover:bg-neutral-800 disabled:opacity-60"
              >
                <RefreshIcon spinning={loading} />
              </button>
            </div>
          </div>

          {showForm && !loading && (
            <DeploymentForm
              hosts={hosts}
              revisions={revisions}
              currentRevisionId={workload?.current_revision_id}
              defaultHostId={defaultHostId}
              onSubmit={handleDeploy}
              onCancel={() => setShowForm(false)}
            />
          )}

          {loading ? (
            <p className="text-sm text-neutral-500">Loading…</p>
          ) : deployments.length === 0 ? (
            <p className="text-sm text-neutral-400">No deployments.</p>
          ) : (
            <DeploymentList
              deployments={deployments}
              hosts={hosts}
              revisions={revisions}
            />
          )}
        </section>
      )}
    </PageShell>
  );
}
