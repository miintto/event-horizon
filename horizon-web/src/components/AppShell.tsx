"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { Footer } from "@/components/Footer";
import {
  CloseIcon,
  HostIcon,
  LogoutIcon,
  MenuIcon,
  OverviewIcon,
  SecretIcon,
  WorkloadIcon,
} from "@/components/Icons";
import { LOGIN_PATH, redirectToLogin } from "@/lib/auth";

interface NavItem {
  href: string;
  label: string;
  Icon: () => React.ReactElement;
}

const NAV_ITEMS: NavItem[] = [
  { href: "/", label: "Overview", Icon: OverviewIcon },
  { href: "/hosts", label: "Hosts", Icon: HostIcon },
  { href: "/workloads", label: "Workloads", Icon: WorkloadIcon },
  { href: "/secrets", label: "Secrets", Icon: SecretIcon },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  const bare = pathname === LOGIN_PATH;

  useEffect(() => {
    if (!open) return;
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }
    document.addEventListener("keydown", onKeyDown);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKeyDown);
      document.body.style.overflow = "";
    };
  }, [open]);

  if (bare) {
    return <>{children}</>;
  }

  return (
    <>
      <aside
        id="app-sidebar"
        className={`fixed inset-y-0 left-0 z-50 flex w-60 flex-col border-r border-neutral-800 bg-neutral-950 transition-transform duration-200 ease-out lg:visible lg:translate-x-0 ${
          open ? "translate-x-0" : "invisible -translate-x-full"
        }`}
      >
        <div className="flex items-center gap-2 px-4 py-3">
          <Link
            href="/"
            onClick={() => setOpen(false)}
            className="flex min-w-0 items-center gap-2"
          >
            <LogoMark />
            <span className="truncate text-base font-semibold text-neutral-100">
              Event Horizon
            </span>
          </Link>
          <button
            type="button"
            onClick={() => setOpen(false)}
            aria-label="Close navigation"
            className="ml-auto cursor-pointer rounded-md p-1.5 text-neutral-400 hover:bg-neutral-800 hover:text-neutral-200 lg:hidden"
          >
            <CloseIcon />
          </button>
        </div>

        <nav className="flex flex-col gap-0.5 px-2 py-2">
          {NAV_ITEMS.map(({ href, label, Icon }) => {
            const active =
              href === "/" ? pathname === "/" : pathname.startsWith(href);
            return (
              <Link
                key={href}
                href={href}
                onClick={() => setOpen(false)}
                aria-current={active ? "page" : undefined}
                className={`flex items-center gap-2.5 rounded-md px-3 py-2 text-sm font-medium ${
                  active
                    ? "bg-accent/15 text-accent"
                    : "text-neutral-400 hover:bg-neutral-900 hover:text-neutral-200"
                }`}
              >
                <Icon />
                {label}
              </Link>
            );
          })}
        </nav>

        <div className="mt-auto px-2 py-3">
          <button
            type="button"
            onClick={redirectToLogin}
            className="flex w-full cursor-pointer items-center gap-2.5 rounded-md px-3 py-2 text-sm font-medium text-neutral-500 hover:bg-neutral-900 hover:text-neutral-300"
          >
            <LogoutIcon />
            Sign out
          </button>
        </div>
      </aside>

      {open && (
        <div
          onClick={() => setOpen(false)}
          aria-hidden="true"
          className="fixed inset-0 z-40 bg-black/60 lg:hidden"
        />
      )}

      <div className="flex min-h-screen flex-col lg:pl-60">
        <header className="sticky top-0 z-30 flex h-14 shrink-0 items-center gap-2.5 border-b border-neutral-800 bg-neutral-950/85 px-4 backdrop-blur lg:hidden">
          <button
            type="button"
            onClick={() => setOpen((v) => !v)}
            aria-label="Toggle navigation"
            aria-expanded={open}
            aria-controls="app-sidebar"
            className="-ml-1.5 cursor-pointer rounded-md p-1.5 text-neutral-300 hover:bg-neutral-800 hover:text-neutral-100"
          >
            <MenuIcon />
          </button>
          <span className="text-base font-semibold text-neutral-100">
            Event Horizon
          </span>
        </header>

        {children}
        <Footer />
      </div>
    </>
  );
}

function LogoMark() {
  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src="/logo.png"
      alt=""
      width={32}
      height={32}
      className="shrink-0 object-contain"
    />
  );
}
