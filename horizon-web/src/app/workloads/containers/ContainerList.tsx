"use client";

import Link from "next/link";

import { StateBadge } from "@/components/Badges";
import { formatDateTime, formatRelative } from "@/lib/format";
import type { Container } from "@/lib/types";

interface ContainerListProps {
  containers: Container[];
  /** 선택된 컨테이너. 없으면 전체 보기 */
  selectedId: number | null;
  hrefFor: (id: number) => string;
}

export function ContainerList({
  containers,
  selectedId,
  hrefFor,
}: ContainerListProps) {
  return (
    <ul className="divide-y divide-neutral-800 overflow-hidden rounded-lg border border-neutral-800 bg-neutral-900">
      {containers.map((container) => {
        const selected = container.id === selectedId;
        return (
          <li key={container.id}>
            <Link
              href={hrefFor(container.id)}
              scroll={false}
              aria-current={selected ? "true" : undefined}
              className={`flex items-center justify-between gap-3 px-4 py-3 hover:bg-neutral-800/60 ${
                selected ? "bg-neutral-800/40" : ""
              }`}
            >
              <div className="min-w-0">
                <p className="truncate font-medium text-neutral-100">
                  {shortId(container)}
                </p>
                <Timestamps container={container} />
              </div>
              <StateBadge state={container.state} />
            </Link>
          </li>
        );
      })}
    </ul>
  );
}

/** 목록·차트 라벨·헤더가 같은 표기를 쓰도록 한 곳에서 만든다 */
export function shortId(container: Container): string {
  return container.docker_id.slice(0, 12);
}

function Timestamps({ container }: { container: Container }) {
  const { created_at, last_seen_at } = container;
  if (!created_at && !last_seen_at) return null;

  return (
    <p className="truncate text-xs text-neutral-500">
      {created_at && (
        <span title={new Date(created_at).toLocaleString()}>
          created {formatDateTime(created_at)}
        </span>
      )}
      {created_at && last_seen_at && " · "}
      {last_seen_at && (
        <span title={new Date(last_seen_at).toLocaleString()}>
          seen {formatRelative(last_seen_at)}
        </span>
      )}
    </p>
  );
}
