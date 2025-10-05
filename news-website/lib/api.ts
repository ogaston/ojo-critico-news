import { Article, DebateSynthesis, FetchArticlesParams, PaginatedArticles } from '../types';

const API_BASE_URL = (process.env.NEWS_API_BASE_URL || 'http://localhost:8000/api/v1').replace(/\/$/, '');

class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

interface FetchOptions {
  query?: Record<string, string | number | undefined>;
  next?: {
    revalidate?: number | false;
    tags?: string[];
  };
}

function buildUrl(path: string): URL {
  return new URL(API_BASE_URL + path);
}

async function fetchFromApi<T>(path: string, options: FetchOptions = {}): Promise<T> {
  const url = buildUrl(path);

  if (options.query) {
    Object.entries(options.query).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        url.searchParams.set(key, String(value));
      }
    });
  }

  try {
    const response = await fetch(url.toString(), {
      headers: {
        Accept: 'application/json'
      },
      next: options.next || { revalidate: 120 }
    });

    if (!response.ok) {
      throw new ApiError(response.status, 'Request failed for ' + url.toString() + ': ' + response.statusText);
    }

    if (response.status === 204) {
      throw new ApiError(204, 'No content');
    }

    return response.json() as Promise<T>;
  } catch (error) {
    // Handle network errors during build time
    if (error instanceof TypeError && error.message.includes('fetch failed')) {
      throw new ApiError(503, 'Service unavailable during build: ' + url.toString());
    }
    throw error;
  }
}

export async function fetchArticles(params: FetchArticlesParams = {}): Promise<PaginatedArticles> {
  return fetchFromApi<PaginatedArticles>('/articles', {
    query: {
      page: params.page || 1,
      page_size: params.pageSize || 12,
      source: params.source,
      category: params.category,
      status: params.status
    },
    next: { revalidate: 240, tags: ['articles'] }
  });
}

export async function fetchArticle(articleId: string): Promise<Article> {
  return fetchFromApi<Article>('/articles/' + articleId, {
    next: { revalidate: 300, tags: ['article-' + articleId] }
  });
}

export async function fetchArticleWithSynthesis(articleId: string): Promise<{ article: Article; synthesis: DebateSynthesis | null; }> {
  const article = await fetchArticle(articleId);
  const synthesis = await fetchSynthesis(articleId).catch((error) => {
    if (error instanceof ApiError && (error.status === 404 || error.status === 204)) {
      return null;
    }

    throw error;
  });

  return { article, synthesis };
}

export async function fetchSynthesis(articleId: string): Promise<DebateSynthesis | null> {
  const candidatePaths = [
    '/articles/' + articleId + '/synthesis',
    '/synthesis/' + articleId,
    '/articles/' + articleId
  ];

  for (const path of candidatePaths) {
    try {
      const query = path.endsWith(articleId) ? { include_synthesis: 'true' } : undefined;
      const payload = await fetchFromApi<
        DebateSynthesis | (Article & { synthesis?: DebateSynthesis | null })
      >(path, {
        query,
        next: { revalidate: 300, tags: ['article-synthesis-' + articleId] }
      });

      if ((payload as DebateSynthesis).article_id) {
        return payload as DebateSynthesis;
      }

      if ((payload as Article & { synthesis?: DebateSynthesis | null }).synthesis !== undefined) {
        return (payload as Article & { synthesis?: DebateSynthesis | null }).synthesis || null;
      }
    } catch (error) {
      if (error instanceof ApiError) {
        if (error.status === 404 || error.status === 204) {
          continue;
        }
      }
      throw error;
    }
  }

  return null;
}

export { ApiError };
