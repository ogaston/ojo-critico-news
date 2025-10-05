"""
MongoDB Pipeline for storing scraped articles
"""
import os
from datetime import datetime
from pymongo import MongoClient, ASCENDING
from pymongo.errors import DuplicateKeyError


class MongoDBPipeline:
    """Pipeline to store articles in MongoDB with deduplication"""

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.client = None
        self.db = None
        self.collection = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=os.getenv('MONGO_URI', 'mongodb://admin:admin123@localhost:27017/'),
            mongo_db=os.getenv('MONGO_DB', 'news_db')
        )

    def open_spider(self, spider):
        """Initialize MongoDB connection when spider opens"""
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.collection = self.db['articles']

        # Create unique index on url and source to prevent duplicates
        self.collection.create_index(
            [('url', ASCENDING), ('source', ASCENDING)],
            unique=True,
            name='url_source_unique'
        )

        # Create indexes for common queries
        self.collection.create_index([('created_at', ASCENDING)])
        self.collection.create_index([('source', ASCENDING)])
        self.collection.create_index([('category', ASCENDING)])

        spider.logger.info(f"MongoDB Pipeline connected to {self.mongo_db}")

    def close_spider(self, spider):
        """Close MongoDB connection when spider closes"""
        if self.client:
            self.client.close()
            spider.logger.info("MongoDB Pipeline connection closed")

    def process_item(self, item, spider):
        """Process and store item in MongoDB"""
        article = dict(item)

        # Add metadata
        article['scraped_at'] = datetime.utcnow()
        article['status'] = 'new'  # Mark as new for debate processing

        try:
            # Insert article
            result = self.collection.insert_one(article)
            spider.logger.info(
                f"Article saved to MongoDB: {article['title'][:50]}... (ID: {result.inserted_id})"
            )
        except DuplicateKeyError:
            # Article already exists (same URL and source)
            spider.logger.warning(
                f"Duplicate article skipped: {article['url']}"
            )
        except Exception as e:
            spider.logger.error(
                f"Error saving article to MongoDB: {str(e)}"
            )

        return item
