"""
Unit tests for MongoDB Pipeline
"""
import unittest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from pymongo.errors import DuplicateKeyError
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipelines import MongoDBPipeline


class TestMongoDBPipeline(unittest.TestCase):
    """Test cases for MongoDBPipeline"""

    def setUp(self):
        """Set up test fixtures"""
        self.pipeline = MongoDBPipeline(
            mongo_uri='mongodb://test:test@localhost:27017/',
            mongo_db='test_db'
        )
        self.mock_spider = Mock()
        self.mock_spider.logger = Mock()

    def test_init(self):
        """Test pipeline initialization"""
        self.assertEqual(self.pipeline.mongo_uri, 'mongodb://test:test@localhost:27017/')
        self.assertEqual(self.pipeline.mongo_db, 'test_db')
        self.assertIsNone(self.pipeline.client)
        self.assertIsNone(self.pipeline.db)
        self.assertIsNone(self.pipeline.collection)

    def test_from_crawler_with_env_vars(self):
        """Test from_crawler class method with environment variables"""
        mock_crawler = Mock()

        with patch.dict(os.environ, {'MONGO_URI': 'mongodb://custom:uri@localhost:27017/', 'MONGO_DB': 'custom_db'}):
            pipeline = MongoDBPipeline.from_crawler(mock_crawler)

            self.assertEqual(pipeline.mongo_uri, 'mongodb://custom:uri@localhost:27017/')
            self.assertEqual(pipeline.mongo_db, 'custom_db')

    def test_from_crawler_with_defaults(self):
        """Test from_crawler class method with default values"""
        mock_crawler = Mock()

        with patch.dict(os.environ, {}, clear=True):
            pipeline = MongoDBPipeline.from_crawler(mock_crawler)

            self.assertEqual(pipeline.mongo_uri, 'mongodb://admin:admin123@localhost:27017/')
            self.assertEqual(pipeline.mongo_db, 'news_db')

    @patch('pipelines.MongoClient')
    def test_open_spider(self, mock_mongo_client):
        """Test opening spider and initializing MongoDB connection"""
        # Setup mocks
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()

        mock_mongo_client.return_value = mock_client
        mock_client.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection

        # Execute
        self.pipeline.open_spider(self.mock_spider)

        # Verify
        mock_mongo_client.assert_called_once_with('mongodb://test:test@localhost:27017/')
        self.assertEqual(self.pipeline.client, mock_client)
        self.assertEqual(self.pipeline.db, mock_db)
        self.assertEqual(self.pipeline.collection, mock_collection)

        # Verify indexes were created
        self.assertEqual(mock_collection.create_index.call_count, 4)

    def test_close_spider(self):
        """Test closing spider and MongoDB connection"""
        # Setup
        mock_client = MagicMock()
        self.pipeline.client = mock_client

        # Execute
        self.pipeline.close_spider(self.mock_spider)

        # Verify
        mock_client.close.assert_called_once()
        self.mock_spider.logger.info.assert_called()

    def test_close_spider_without_client(self):
        """Test closing spider when no client exists"""
        self.pipeline.client = None

        # Should not raise exception
        self.pipeline.close_spider(self.mock_spider)

    def test_process_item_success(self):
        """Test successfully processing and storing an item"""
        # Setup
        mock_collection = MagicMock()
        mock_result = Mock()
        mock_result.inserted_id = 'test_id_123'
        mock_collection.insert_one.return_value = mock_result

        self.pipeline.collection = mock_collection

        # Create test item
        test_item = {
            'title': 'Test Article Title',
            'content': 'Test content',
            'url': 'https://example.com/article',
            'source': 'test_source'
        }

        # Execute
        with patch('pipelines.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2024, 1, 1, 12, 0, 0)
            result = self.pipeline.process_item(test_item, self.mock_spider)

        # Verify
        self.assertEqual(result, test_item)
        mock_collection.insert_one.assert_called_once()

        # Verify the article dict passed to insert_one has metadata
        inserted_article = mock_collection.insert_one.call_args[0][0]
        self.assertEqual(inserted_article['title'], 'Test Article Title')
        self.assertEqual(inserted_article['scraped_at'], datetime(2024, 1, 1, 12, 0, 0))
        self.assertEqual(inserted_article['status'], 'new')

    def test_process_item_duplicate(self):
        """Test processing duplicate item"""
        # Setup
        mock_collection = MagicMock()
        mock_collection.insert_one.side_effect = DuplicateKeyError('Duplicate key error')

        self.pipeline.collection = mock_collection

        test_item = {
            'title': 'Duplicate Article',
            'url': 'https://example.com/duplicate',
            'source': 'test_source'
        }

        # Execute
        with patch('pipelines.datetime'):
            result = self.pipeline.process_item(test_item, self.mock_spider)

        # Verify
        self.assertEqual(result, test_item)
        self.mock_spider.logger.warning.assert_called()

    def test_process_item_error(self):
        """Test processing item with database error"""
        # Setup
        mock_collection = MagicMock()
        mock_collection.insert_one.side_effect = Exception('Database connection error')

        self.pipeline.collection = mock_collection

        test_item = {
            'title': 'Error Article',
            'url': 'https://example.com/error',
            'source': 'test_source'
        }

        # Execute
        with patch('pipelines.datetime'):
            result = self.pipeline.process_item(test_item, self.mock_spider)

        # Verify
        self.assertEqual(result, test_item)
        self.mock_spider.logger.error.assert_called()


if __name__ == '__main__':
    unittest.main()
