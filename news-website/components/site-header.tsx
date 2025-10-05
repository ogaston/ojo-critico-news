import Link from 'next/link';

export function SiteHeader() {
  const today = new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric'
  });

  return (
    <header className="border-b border-ink/10 pb-6">
      <div className="flex items-center justify-between gap-4 text-xs uppercase tracking-[0.3em] text-ink/60">
        <span>{today}</span>
        <span>Edition 01</span>
      </div>
      <div className="mt-4 flex flex-wrap items-end justify-between gap-4">
        <Link href="/" className="font-serif text-4xl uppercase tracking-[0.25em] text-ink">
          Ojo Crítico
        </Link>
        <nav className="flex items-center gap-6 text-sm uppercase tracking-[0.2em] text-ink/70">
          <Link href="/" className="hover:text-accent">
            Home
          </Link>
          <a
            href="https://github.com/dominguez-dev"
            className="hover:text-accent"
            target="_blank"
            rel="noreferrer"
          >
            Investigations
          </a>
          <a
            href="mailto:newsdesk@ojo-critico.com"
            className="hover:text-accent"
          >
            Tip Line
          </a>
        </nav>
      </div>
    </header>
  );
}
