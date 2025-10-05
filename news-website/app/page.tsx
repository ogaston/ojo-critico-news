import { fetchArticles } from '../lib/api';
import { ArticleList } from '../components/article-list';

// Force dynamic rendering to avoid build-time API calls
export const dynamic = 'force-dynamic';

export default async function HomePage() {
  let articles = [];
  
  try {
    const feed = await fetchArticles({ pageSize: 7 });
    articles = feed.articles || [];
  } catch (error) {
    // Gracefully handle API unavailability during build or runtime
    console.warn('Failed to fetch articles:', error);
    articles = [];
  }

  return (
    <div className="space-y-12">
      <section className="border-b border-ink/10 pb-8">
        <div className="max-w-3xl space-y-4">
          <p className="text-xs uppercase tracking-[0.35em] text-ink/50">Investigative desk</p>
          <h1 className="font-serif text-4xl text-ink sm:text-5xl">
            Daily scrutiny of Dominican headlines with debate-backed context.
          </h1>
          <p className="text-base leading-relaxed text-ink/70">
            Each story passes through an AI moderated debate that challenges claims, highlights corroboration,
            and surfaces a transparent verdict. Explore the latest dispatches below.
          </p>
        </div>
      </section>

      <ArticleList articles={articles} />
    </div>
  );
}
