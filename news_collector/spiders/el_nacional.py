import scrapy
from items import ArticleItem
from datetime import datetime


class ElNacionalSpider(scrapy.Spider):
    name = 'el-nacional-spider'
    allowed_domains = ['elnacional.com.do']
    start_urls = ['https://elnacional.com.do/']

    def parse(self, response):
        """
        Parse the main page and extract articles from .utf_featured_post_area section
        """
        # Select articles within the .utf_featured_post_area section
        articles = response.css('.utf_featured_post_area article, .utf_featured_post_area .post, .utf_featured_post_area .entry')
        
        if not articles:
            # Fallback: try to find any clickable elements with titles in utf_featured_post_area
            articles = response.css('.utf_featured_post_area a[href*="/"]')
        
        for article in articles:
            item = ArticleItem()
            
            # Extract title - try multiple selectors
            title = (article.css('h1::text, h2::text, h3::text, .title::text, .entry-title::text').get() or 
                    article.css('a::attr(title)').get() or
                    article.css('img::attr(alt)').get())
            
            if title:
                item['title'] = title.strip()
                
                # Extract short description
                item['short_description'] = (
                    article.css('p::text, .excerpt::text, .summary::text, .entry-summary::text').get() or
                    article.css('.post-excerpt::text, .entry-content p::text').get() or ""
                ).strip()
                
                # Extract category
                category = (
                    article.css('.category::text, .cat-links a::text, .post-category::text').get() or
                    article.css('[class*="category"]::text, [class*="cat"]::text').get() or ""
                ).strip()
                item['category'] = category if category else "undefined"
                
                # Extract photo URL
                photo_url = article.css('img::attr(src), img::attr(data-src)').get()
                if photo_url:
                    item['photo_url'] = response.urljoin(photo_url)
                else:
                    item['photo_url'] = ""
                
                # Get article URL
                article_url = (article.css('a::attr(href)').get() or 
                             article.css('h1 a::attr(href), h2 a::attr(href), h3 a::attr(href)').get())
                
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
        
        # Extract full content - try multiple selectors for El Nacional
        content_selectors = [
            '.entry-content',
            '.post-content', 
            '.article-content',
            '.content',
            '.single-content',
            '.post-body',
            'article .content',
            '.main-content p'
        ]
        
        content = ""
        for selector in content_selectors:
            content_parts = response.css(f'{selector} p::text').getall()
            if content_parts:
                content = ' '.join(content_parts).strip()
                break
        
        if not content:
            # Fallback: try to get any paragraph text
            content_parts = response.css('article p::text, .content p::text, main p::text').getall()
            content = ' '.join(content_parts).strip()
        
        item['content'] = content
        
        # Extract author - try multiple selectors
        author_selectors = [
            '.author::text',
            '.byline::text', 
            '.post-author::text',
            '.entry-author::text',
            '.author-name::text',
            '[class*="author"]::text',
            '.vcard .fn::text'
        ]
        
        author = ""
        for selector in author_selectors:
            author = response.css(selector).get()
            if author:
                author = author.strip()
                break
        
        item['author'] = author if author else "unknown"
        
        # Extract publication date - try multiple selectors
        date_selectors = [
            '.date::text',
            '.publish-date::text',
            '.entry-date::text',
            '.post-date::text', 
            '.published::text',
            'time::text',
            'time::attr(datetime)',
            '[class*="date"]::text'
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
        item['source'] = 'el_nacional'

        yield item
