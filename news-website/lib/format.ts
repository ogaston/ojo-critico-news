export function formatDate(value: string | null | undefined, locale = 'en-US'): string {
  if (!value) {
    return 'Date unavailable';
  }

  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }

  return parsed.toLocaleDateString(locale, {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
}

export function splitParagraphs(content: string | null | undefined): string[] {
  if (!content) {
    return [];
  }

  return content
    .split(/\n+/)
    .map((paragraph) => paragraph.trim())
    .filter(Boolean);
}

export function formatProbability(value: number | undefined | null): string {
  if (typeof value !== 'number' || Number.isNaN(value)) {
    return '—';
  }

  const percentage = value <= 1 ? value * 100 : value;
  return percentage.toFixed(0) + '%';
}
