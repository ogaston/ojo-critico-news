# News Collector Spiders

This project contains spiders to extract news articles from multiple Dominican news websites:

- **Listín Diario** (https://listindiario.com/) - focuses on `.home-boards` section
- **El Nacional** (https://elnacional.com.do/) - focuses on `.utf_featured_post_area` section

## Extracted Fields

The spider extracts the following information from each article:

- **title**: Article headline
- **short_description**: Brief description or excerpt
- **category**: Article category/section
- **photo_url**: URL of the main article image
- **content**: Full article content
- **author**: Article author
- **created_at**: Publication date
- **url**: Article URL for reference

## Project Structure

```
news_collector/
├── spiders/
│   ├── __init__.py
│   ├── items.py: Scrapy item definitions
│   ├── listin_diario.py: Listín Diario spider
│   └── el_nacional.py: El Nacional spider
├── outputs/: Output directory for scraped data
├── run_spider.py: Runner script for both spiders
├── requirements.txt: Python dependencies
└── SPIDER_README.md: This documentation
```

## Installation

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Using the runner script (Recommended)
```bash
python run_spider.py
```

This will run both spiders sequentially and save outputs to the `outputs/` directory.

## Output

The spiders save extracted articles to JSON files in the `outputs/` directory:
- `outputs/listin_diario_articles.json`: Articles from Listín Diario
- `outputs/el_nacional_articles.json`: Articles from El Nacional

Example output structure:
```json
[
  {
    "title": "Article Title",
    "short_description": "Brief description of the article...",
    "category": "Politics",
    "photo_url": "https://listindiario.com/images/article.jpg",
    "content": "Full article content...",
    "author": "Author Name",
    "created_at": "2024-01-15",
    "url": "https://listindiario.com/article-url"
  }
]
```

## Spider Features

- **Robust Selector Strategy**: Uses multiple CSS selectors as fallbacks to handle different page layouts
- **Respectful Crawling**: Implements delays and throttling to avoid overwhelming the server
- **Two-Stage Extraction**: 
  1. Extracts basic info from listing pages
  2. Follows article links to get full content, author, and date
- **Error Handling**: Gracefully handles missing elements and malformed pages
- **URL Normalization**: Properly handles relative URLs

## Configuration

The spider includes several configurable settings in `run_spider.py`:

- `DOWNLOAD_DELAY`: Delay between requests (default: 1 second)
- `CONCURRENT_REQUESTS`: Number of concurrent requests (default: 16)
- `USER_AGENT`: Browser user agent string
- `ROBOTSTXT_OBEY`: Respect robots.txt (default: True)

## Customization

To modify the spider for different selectors or additional fields:

1. Update the CSS selectors in `listin_diario.py`
2. Add new fields to `ArticleItem` in `items.py`
3. Update the extraction logic in the `parse` and `parse_article` methods

## Notes

- The spider focuses on the `.home-boards` section as requested
- It uses multiple fallback selectors to handle different article layouts
- Respects the website's robots.txt and implements polite crawling practices
- Handles both relative and absolute URLs properly
