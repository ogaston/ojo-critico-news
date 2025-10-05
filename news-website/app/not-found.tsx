import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="py-24 text-center">
      <p className="text-xs uppercase tracking-[0.35em] text-ink/50">404 — Missing dispatch</p>
      <h2 className="mt-4 font-serif text-4xl text-ink">We could not locate that story.</h2>
      <p className="mt-3 text-base text-ink/70">
        The requested article is not available or has not been cleared for publication yet.
      </p>
      <Link
        href="/"
        className="mt-6 inline-block border border-ink/20 px-4 py-2 text-xs uppercase tracking-[0.25em] text-ink transition hover:border-ink hover:text-accent"
      >
        Return to the newsroom
      </Link>
    </div>
  );
}
