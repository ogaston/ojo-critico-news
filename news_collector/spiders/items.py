import scrapy


class ArticleItem(scrapy.Item):
    """
    Item definition for news articles
    """
    title = scrapy.Field()
    short_description = scrapy.Field()
    category = scrapy.Field()
    photo_url = scrapy.Field()
    content = scrapy.Field()
    author = scrapy.Field()
    created_at = scrapy.Field()
    url = scrapy.Field()  # Store the article URL for reference
    source = scrapy.Field()  # Source newspaper (listin_diario, el_nacional, etc.)
