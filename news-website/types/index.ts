export interface Article {
  id: string;
  title: string;
  short_description: string;
  category: string;
  photo_url: string;
  content: string;
  author: string;
  created_at: string;
  url: string;
  source: string;
  scraped_at?: string;
  status: string;
  synthesis_id?: string;
}

export interface PaginatedArticles {
  total: number;
  page: number;
  page_size: number;
  articles: Article[];
}

export interface DebateSynthesis {
  id: string;
  article_id: string;
  verdict?: string;
  probability_true?: number;
  created_at?: string;
  synthesis_report?: {
    report?: string;
    verdict?: string;
  };
  analysis_report?: {
    prob_true?: number;
    verdict?: string;
    rationale?: string;
    raw_analysis?: string;
    [key: string]: unknown;
  };
  report?: string;
}

export interface FetchArticlesParams {
  page?: number;
  pageSize?: number;
  source?: string;
  category?: string;
  status?: string;
}
