export function Footer() {
  const year = new Date().getFullYear();
  return (
    <footer className="mt-4 border-t border-neutral-800">
      <div className="mx-auto flex w-full max-w-5xl flex-col gap-1 px-4 py-6 sm:flex-row sm:items-center sm:justify-between">
        <p className="py-2">
          <span className="font-medium text-neutral-400">Event Horizon</span>
        </p>
        <p className="text-sm text-neutral-500">Copyright © miintto {year}</p>
      </div>
    </footer>
  );
}
