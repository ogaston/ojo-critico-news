import Image from 'next/image';
import Link from 'next/link';
import clsx from 'clsx';
import { Article } from '../types';
import { formatDate } from '../lib/format';

interface ArticleCardProps {
  article: Article;
  variant?: 'featured' | 'standard' | 'compact';
}

export function ArticleCard({ article, variant = 'standard' }: ArticleCardProps) {
  const hasImage = Boolean(article.photo_url);
  const containerClasses = clsx(
    'group overflow-hidden border border-ink/10 bg-white transition duration-200',
    'hover:-translate-y-1 hover:shadow-subtle',
    {
      'md:flex md:min-h-[320px]': variant === 'featured'
    }
  );

  return (
    <article className={containerClasses}>
      {hasImage && (
        <div className={clsx('relative', {
          'h-80 w-full md:h-auto md:w-1/2': variant === 'featured',
          'h-56 w-full': variant !== 'featured'
        })}>
          <Image
            src={article.photo_url}
            alt={article.title}
            fill
            className="object-cover"
            sizes="(min-width: 768px) 50vw, 100vw"
          />
        </div>
      )}
      <div
        className={clsx('flex flex-1 flex-col justify-between', {
          'p-10': variant === 'featured',
          'p-6': variant === 'standard',
          'p-5': variant === 'compact'
        })}
      >
        <div className="space-y-3">
          <p className="text-xs uppercase tracking-[0.25em] text-ink/50">{article.category}</p>
          <Link href={'/articles/' + article.id} prefetch className="block font-serif text-2xl leading-tight text-ink">
            {article.title}
          </Link>
          {article.short_description && (
            <p className="text-sm leading-relaxed text-ink/70">
              {article.short_description}
            </p>
          )}
        </div>
        <div className="mt-6 flex flex-wrap items-center gap-3 text-xs uppercase tracking-[0.2em] text-ink/50">
          <span>{article.source}</span>
          <span className="hidden h-3 w-px bg-ink/20 sm:block" aria-hidden="true" />
          <span>{formatDate(article.created_at)}</span>
        </div>
      </div>
    </article>
  );
}
