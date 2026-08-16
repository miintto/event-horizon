"use client";

import { formatCores, MIB } from "@/lib/format";
import type { ContainerSpec, WorkloadRevision } from "@/lib/types";

export function RevisionDetail({ revision }: { revision: WorkloadRevision }) {
  const spec = revision.spec;

  return (
    <section className="mt-8">
      <h2 className="mb-3 text-xs font-medium tracking-wide text-neutral-500 uppercase">
        Definition — rev {revision.revision}
      </h2>

      <div className="divide-y divide-neutral-800 rounded-lg border border-neutral-800 bg-neutral-900">
        <Section label="Image" count={1}>
          <Row>
            <Mono>{revision.image}</Mono>
          </Row>
        </Section>

        <Section label="CPU" count={revision.cpu_limit ? 1 : 0}>
          {revision.cpu_limit && (
            <Row>
              <Mono>{formatCores(revision.cpu_limit)}</Mono>
              <Note>cores</Note>
            </Row>
          )}
        </Section>

        <Section label="Memory" count={revision.memory_limit ? 1 : 0}>
          {revision.memory_limit && (
            <Row>
              <Mono>{revision.memory_limit / MIB}</Mono>
              <Note>MiB</Note>
            </Row>
          )}
        </Section>

        <Section label="Ports" count={spec.ports?.length}>
          {spec.ports?.map((port, i) => (
            <Row key={i}>
              <Mono>
                {port.host_port != null ? `${port.host_port} → ` : ""}
                {port.container_port}/{port.protocol}
              </Mono>
              {port.host_port == null && <Note>not published</Note>}
            </Row>
          ))}
        </Section>

        <Section label="Environment" count={spec.env?.length}>
          {spec.env?.map((env) => (
            <Row key={env.name}>
              <Mono>{env.name}</Mono>
              <Value>{env.value}</Value>
            </Row>
          ))}
        </Section>

        <Section label="Secrets" count={spec.secrets?.length}>
          {spec.secrets?.map((secret) => (
            <Row key={secret.name}>
              <Mono>{secret.name}</Mono>
              <Note>from {secret.ref}</Note>
            </Row>
          ))}
        </Section>

        <Section label="Mounts" count={spec.mounts?.length}>
          {spec.mounts?.map((mount, i) => (
            <Row key={i}>
              <Mono>
                {mount.source} → {mount.target}
              </Mono>
              <Note>
                {mount.type}
                {mount.read_only ? " · read-only" : ""}
              </Note>
            </Row>
          ))}
        </Section>

        <Section label="Command" count={spec.command?.length}>
          {spec.command && (
            <Row>
              <Mono>{spec.command.join(" ")}</Mono>
            </Row>
          )}
        </Section>

        <Section label="Entrypoint" count={spec.entrypoint?.length}>
          {spec.entrypoint && (
            <Row>
              <Mono>{spec.entrypoint.join(" ")}</Mono>
            </Row>
          )}
        </Section>

        <Section label="Healthcheck" count={spec.healthcheck ? 1 : 0}>
          {spec.healthcheck && (
            <Row>
              <Mono>{spec.healthcheck.test.join(" ")}</Mono>
              <Note>{formatHealthcheck(spec.healthcheck)}</Note>
            </Row>
          )}
        </Section>

        <Section label="Restart policy" count={spec.restart_policy ? 1 : 0}>
          {spec.restart_policy && (
            <Row>
              <Mono>{spec.restart_policy.name}</Mono>
              {spec.restart_policy.max_retry > 0 && (
                <Note>max {spec.restart_policy.max_retry} retries</Note>
              )}
            </Row>
          )}
        </Section>

        <Section label="Network" count={spec.network_mode ? 1 : 0}>
          {spec.network_mode && (
            <Row>
              <Mono>{spec.network_mode}</Mono>
            </Row>
          )}
        </Section>

        <Section label="Logging" count={spec.log ? 1 : 0}>
          {spec.log && (
            <Row>
              <Mono>{spec.log.driver}</Mono>
              <Note>{formatOptions(spec.log.options)}</Note>
            </Row>
          )}
        </Section>

        <Section label="Labels" count={countOf(spec.labels)}>
          {Object.entries(spec.labels ?? {}).map(([key, value]) => (
            <Row key={key}>
              <Mono>{key}</Mono>
              <Value>{value}</Value>
            </Row>
          ))}
        </Section>
      </div>
    </section>
  );
}

function Section({
  label,
  count,
  children,
}: {
  label: string;
  count?: number;
  children: React.ReactNode;
}) {
  return (
    <div className="flex gap-4 px-4 py-3">
      <p className="w-24 shrink-0 text-sm text-neutral-500 lg:w-32">{label}</p>
      {count ? (
        <div className="min-w-0 flex-1 space-y-1">{children}</div>
      ) : (
        <p className="text-sm text-neutral-600">—</p>
      )}
    </div>
  );
}

function Row({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex flex-wrap items-baseline gap-x-3">{children}</div>
  );
}

function Mono({ children }: { children: React.ReactNode }) {
  return (
    <span className="font-mono text-sm break-all text-neutral-100">
      {children}
    </span>
  );
}

function Value({ children }: { children: React.ReactNode }) {
  return (
    <span className="font-mono text-sm break-all text-neutral-400">
      {children}
    </span>
  );
}

function Note({ children }: { children: React.ReactNode }) {
  return <span className="text-sm text-neutral-500">{children}</span>;
}

function countOf(record?: Record<string, string>): number {
  return Object.keys(record ?? {}).length;
}

function formatHealthcheck(check: NonNullable<ContainerSpec["healthcheck"]>) {
  const parts = [];
  if (check.interval_secs) parts.push(`every ${check.interval_secs}s`);
  if (check.timeout_secs) parts.push(`timeout ${check.timeout_secs}s`);
  if (check.retries != null) parts.push(`${check.retries} retries`);
  return parts.join(" · ");
}

function formatOptions(options: Record<string, string>): string {
  return Object.entries(options)
    .map(([key, value]) => `${key}=${value}`)
    .join(" · ");
}
