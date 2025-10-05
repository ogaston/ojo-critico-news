import { Article } from '../types';
import { ArticleCard } from './article-card';

interface ArticleListProps {
  articles: Article[];
}

export function ArticleList({ articles }: ArticleListProps) {
  if (!articles.length) {
    return (
      <div className="py-24 text-center text-ink/60">
        <p className="text-sm uppercase tracking-[0.3em]">No stories yet</p>
        <p className="mt-3 text-lg">We will publish headlines once the newsroom receives its first dispatch.</p>
      </div>
    );
  }

  const [hero, ...others] = articles;

  return (
    <div className="space-y-12">
      <section>
        <ArticleCard article={hero} variant="featured" />
      </section>

      {others.length > 0 && (
        <section className="grid gap-8 md:grid-cols-2">
          {others.map((article) => (
            <ArticleCard key={article.id} article={article} variant="standard" />
          ))}
        </section>
      )}
    </div>
  );
}
