export function PageShell({ children }: { children: React.ReactNode }) {
  return (
    <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-6 sm:py-8">
      {children}
    </main>
  );
}

export function PageHeader({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children?: React.ReactNode;
}) {
  return (
    <header className="mb-5">
      <div className="flex flex-wrap items-center gap-x-3 gap-y-2">
        <h1 className="text-xl font-semibold text-neutral-100 sm:text-2xl">
          {title}
        </h1>
        {children}
      </div>
      {subtitle && (
        <p className="mt-1 truncate text-xs text-neutral-500">{subtitle}</p>
      )}
    </header>
  );
}

export function NewButton({
  label,
  onClick,
}: {
  label: string;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="ml-auto cursor-pointer rounded-md px-2.5 py-1 text-sm font-medium text-neutral-400 hover:bg-neutral-800 hover:text-neutral-200"
    >
      + New {label}
    </button>
  );
}

export function ErrorBox({ children }: { children: React.ReactNode }) {
  return (
    <div className="rounded-md border border-red-900/50 bg-red-950/40 p-4 text-sm text-red-300">
      {children}
    </div>
  );
}
