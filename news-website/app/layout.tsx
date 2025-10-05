import type { Metadata } from 'next';
import { Playfair_Display, Source_Sans_3 } from 'next/font/google';
import './globals.css';
import { SiteHeader } from '../components/site-header';

const heading = Playfair_Display({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
  variable: '--font-serif'
});

const body = Source_Sans_3({
  subsets: ['latin'],
  weight: ['300', '400', '500', '600'],
  variable: '--font-sans'
});

export const metadata: Metadata = {
  title: 'Ojo Crítico | Investigative News Desk',
  description: 'Curated Dominican news with critical debate synthesis.'
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  const classes = [heading.variable, body.variable].join(' ');

  return (
    <html lang="en" className={classes}>
      <body className="min-h-screen bg-parchment text-ink">
        <div className="mx-auto flex min-h-screen max-w-6xl flex-col px-4 pb-16 pt-8 sm:px-6 lg:px-8">
          <SiteHeader />
          <main className="mt-10 flex-1">{children}</main>
          <footer className="mt-12 border-t border-ink/10 pt-6 text-xs uppercase tracking-[0.2em] text-ink/50">
            <div className="flex flex-wrap justify-between gap-2">
              <span>Ojo Crítico — Investigative Dominion</span>
              <span>Crafted with Next.js and FastAPI</span>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
