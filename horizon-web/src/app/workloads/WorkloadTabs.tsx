"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const TABS = [
  { href: "/workloads/containers", label: "Containers" },
  { href: "/workloads/revisions", label: "Revisions" },
];

export function WorkloadTabs({ workloadId }: { workloadId: number | null }) {
  const pathname = usePathname();

  return (
    <nav className="mb-6 flex gap-1 border-b border-neutral-800">
      {TABS.map(({ href, label }) => {
        const active = pathname === href;
        return (
          <Link
            key={href}
            href={
              workloadId == null ? href : `${href}?workload_id=${workloadId}`
            }
            aria-current={active ? "page" : undefined}
            className={`-mb-px border-b-2 px-3 py-2 text-sm font-medium ${
              active
                ? "border-accent text-accent"
                : "border-transparent text-neutral-500 hover:text-neutral-300"
            }`}
          >
            {label}
          </Link>
        );
      })}
    </nav>
  );
}
