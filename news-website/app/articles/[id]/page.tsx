import type { Metadata } from 'next';
import Image from 'next/image';
import { notFound } from 'next/navigation';
import { ApiError, fetchArticle, fetchArticleWithSynthesis } from '../../../lib/api';
import { formatDate, splitParagraphs } from '../../../lib/format';
import { SynthesisPanel } from '../../../components/synthesis-panel';

// Force dynamic rendering to avoid build-time API calls
export const dynamic = 'force-dynamic';

interface PageProps {
  params: { id: string };
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  try {
    const article = await fetchArticle(params.id);
    return {
      title: article.title + ' | Ojo Crítico',
      description: article.short_description || article.content.slice(0, 160)
    };
  } catch (error) {
    if (error instanceof ApiError && (error.status === 404 || error.status === 503)) {
      return {
        title: 'Story not found | Ojo Crítico'
      };
    }

    // Don't throw during build time - return default metadata
    return {
      title: 'Ojo Crítico',
      description: 'Dominican news with AI-moderated debate context'
    };
  }
}

export default async function ArticleDetailPage({ params }: PageProps) {
  try {
    const { article, synthesis } = await fetchArticleWithSynthesis(params.id);
    const paragraphs = splitParagraphs(article.content);

    return (
      <div className="grid gap-12 lg:grid-cols-[2fr_1fr]">
        <article className="space-y-6">
          <header className="space-y-4">
            <p className="text-xs uppercase tracking-[0.35em] text-ink/50">{article.category}</p>
            <h1 className="font-serif text-4xl leading-tight text-ink sm:text-5xl">{article.title}</h1>
            <div className="flex flex-wrap items-center gap-3 text-xs uppercase tracking-[0.2em] text-ink/50">
              <span>{article.source}</span>
              <span className="hidden h-3 w-px bg-ink/20 sm:block" aria-hidden="true" />
              <span>{formatDate(article.created_at)}</span>
              {article.author && (
                <>
                  <span className="hidden h-3 w-px bg-ink/20 sm:block" aria-hidden="true" />
                  <span>{article.author}</span>
                </>
              )}
            </div>
          </header>

          {article.photo_url && (
            <div className="relative h-96 w-full overflow-hidden border border-ink/10">
              <Image
                src={article.photo_url}
                alt={article.title}
                fill
                sizes="(min-width: 1024px) 800px, 100vw"
                className="object-cover"
              />
            </div>
          )}

          <div className="space-y-4 text-lg leading-relaxed text-ink/80">
            {paragraphs.length
              ? paragraphs.map((paragraph, index) => (
                  <p key={index}>{paragraph}</p>
                ))
              : article.content && <p>{article.content}</p>}
          </div>

          <div className="mt-10 flex flex-wrap items-center gap-4 border-t border-ink/10 pt-6 text-xs uppercase tracking-[0.25em] text-ink/60">
            {article.url && (
              <a
                href={article.url}
                className="rounded-sm border border-ink/20 px-4 py-2 tracking-[0.2em] text-ink transition hover:border-ink hover:text-accent"
                target="_blank"
                rel="noreferrer"
              >
                Read Original Source
              </a>
            )}
            <span>Status: {article.status || 'new'}</span>
          </div>
        </article>

        <SynthesisPanel synthesis={synthesis} />
      </div>
    );
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      notFound();
    }

    throw error;
  }
}
