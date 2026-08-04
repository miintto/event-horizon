import { GitHubIcon, MailIcon } from "@/components/Icons";

export function Footer() {
  const year = new Date().getFullYear();
  return (
    <footer className="my-4 border-t border-neutral-800">
      <div className="mx-auto flex w-full max-w-5xl flex-col gap-1 px-4 py-6 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-col gap-1 py-2">
          <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:gap-3">
            <a
              href="https://github.com/miintto/event-horizon"
              target="_blank"
              rel="noreferrer noopener"
              className="inline-flex w-fit items-center gap-1.5 text-sm text-neutral-500 hover:text-neutral-400"
            >
              <GitHubIcon />
              GitHub
            </a>
            <a
              href="mailto:miintto.log@gmail.com"
              className="inline-flex w-fit items-center gap-1.5 text-sm text-neutral-500 hover:text-neutral-400"
            >
              <MailIcon />
              miintto.log@gmail.com
            </a>
          </div>
        </div>
        <p className="text-sm text-neutral-600">Copyright © miintto {year}</p>
      </div>
    </footer>
  );
}
