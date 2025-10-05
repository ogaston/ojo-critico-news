import scrapy
from items import ArticleItem
from datetime import datetime


class ListinDiarioSpider(scrapy.Spider):
    name = 'listin-diario-spider'
    allowed_domains = ['listindiario.com']
    start_urls = ['https://listindiario.com']

    def parse(self, response):
        """
        Parse the main page and extract articles from .home-boards section
        """
        # Select articles within the .home-boards section
        # Use the specific selectors for Listín Diario
        articles = response.css('.home-boards .c-article__title a')
        
        for article in articles:
            item = ArticleItem()
            
            # Extract title from the specific selector
            title = article.css('::text').get()
            
            if title:
                item['title'] = title.strip()
                
                # Extract short description - try to find it in the same article container
                # Look for description in the parent container
                article_container = article.xpath('./ancestor::*[contains(@class, "c-article")]')
                item['short_description'] = (
                    article_container.css('.c-article__excerpt::text, .c-article__summary::text, p::text').get() or ""
                ).strip()
                
                # Extract category using the specific selector
                category = article_container.css('.c-article__epigraph::text').get()
                item['category'] = category.strip() if category else "undefined"
                
                # Extract photo URL from the article container
                photo_url = article_container.css('img::attr(src), img::attr(data-src)').get()
                if photo_url:
                    item['photo_url'] = response.urljoin(photo_url)
                else:
                    item['photo_url'] = ""
                
                # Get article URL
                article_url = article.css('::attr(href)').get()
                
                if article_url:
                    article_url = response.urljoin(article_url)
                    item['url'] = article_url
                    
                    # Follow the link to get full content
                    yield response.follow(
                        article_url, 
                        self.parse_article, 
                        meta={'item': item},
                        dont_filter=True
                    )
                else:
                    # If no URL found, skip this record since we need both title and content
                    # and we can't get content without following the article link
                    pass

    def parse_article(self, response):
        """
        Parse individual article page to extract full content, author, and date
        """
        item = response.meta['item']
        
        # Extract full content using the specific selector
        content_parts = response.css('.c-article__free .c-detail__body p::text').getall()
        if content_parts:
            item['content'] = ' '.join(content_parts).strip()
        else:
            # Fallback: try to get any paragraph text from the content area
            content_parts = response.css('.c-article__free p::text, .c-detail__body p::text').getall()
            item['content'] = ' '.join(content_parts).strip() if content_parts else ""
        
        # Extract author using the specific selector
        author = response.css('.detail__bio__name::text').get()
        item['author'] = author.strip() if author else "unknown"
        
        # Extract publication date - try to find it, if not available set today's date
        date_selectors = [
            '.date::text',
            '.publish-date::text',
            '.publication-date::text', 
            '.created-at::text',
            '.timestamp::text',
            'time::text',
            'time::attr(datetime)',
            '[class*="date"]::text',
            '.post-date::text',
            '.article-date::text'
        ]
        
        created_at = ""
        for selector in date_selectors:
            created_at = response.css(selector).get()
            if created_at:
                created_at = created_at.strip()
                break
        
        # If no date found, set today's date in DD/MM/YYYY format
        item['created_at'] = created_at if created_at else datetime.now().strftime("%d/%m/%Y")

        # Add source identifier
        item['source'] = 'listin_diario'

        yield item