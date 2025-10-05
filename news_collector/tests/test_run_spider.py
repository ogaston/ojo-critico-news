"""
Unit tests for CustomJsonPipeline
"""
import unittest
import tempfile
import json
import os
import shutil
from unittest.mock import Mock
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from run_spider import CustomJsonPipeline


class TestCustomJsonPipeline(unittest.TestCase):
    """Test cases for CustomJsonPipeline"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.output_file = os.path.join(self.temp_dir, 'outputs', 'test_output.json')
        self.pipeline = CustomJsonPipeline(self.output_file)
        self.mock_spider = Mock()
        self.mock_spider.name = 'test_spider'

    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_init(self):
        """Test pipeline initialization"""
        self.assertEqual(self.pipeline.output_file, self.output_file)
        self.assertEqual(self.pipeline.items, [])

    def test_from_crawler(self):
        """Test from_crawler class method"""
        mock_crawler = Mock()
        mock_crawler.settings.get.return_value = '/test/path/output.json'

        pipeline = CustomJsonPipeline.from_crawler(mock_crawler)

        self.assertEqual(pipeline.output_file, '/test/path/output.json')
        mock_crawler.settings.get.assert_called_once_with('OUTPUT_FILE')

    def test_open_spider(self):
        """Test opening spider initializes items list"""
        self.pipeline.items = ['some', 'existing', 'items']

        self.pipeline.open_spider(self.mock_spider)

        self.assertEqual(self.pipeline.items, [])

    def test_process_item(self):
        """Test processing item adds it to items list"""
        test_item = {
            'title': 'Test Article',
            'content': 'Test content',
            'url': 'https://example.com/test'
        }

        result = self.pipeline.process_item(test_item, self.mock_spider)

        self.assertEqual(result, test_item)
        self.assertEqual(len(self.pipeline.items), 1)
        self.assertEqual(self.pipeline.items[0], test_item)

    def test_process_multiple_items(self):
        """Test processing multiple items"""
        items = [
            {'title': 'Article 1', 'url': 'https://example.com/1'},
            {'title': 'Article 2', 'url': 'https://example.com/2'},
            {'title': 'Article 3', 'url': 'https://example.com/3'}
        ]

        for item in items:
            self.pipeline.process_item(item, self.mock_spider)

        self.assertEqual(len(self.pipeline.items), 3)
        self.assertEqual(self.pipeline.items, items)

    def test_close_spider_creates_directory(self):
        """Test that close_spider creates output directory if it doesn't exist"""
        self.assertFalse(os.path.exists(os.path.dirname(self.output_file)))

        self.pipeline.close_spider(self.mock_spider)

        self.assertTrue(os.path.exists(os.path.dirname(self.output_file)))

    def test_close_spider_writes_json(self):
        """Test that close_spider writes JSON file correctly"""
        test_items = [
            {'title': 'Article 1', 'content': 'Content 1', 'url': 'https://example.com/1'},
            {'title': 'Article 2', 'content': 'Content 2', 'url': 'https://example.com/2'}
        ]

        self.pipeline.items = test_items
        self.pipeline.close_spider(self.mock_spider)

        # Verify file exists
        self.assertTrue(os.path.exists(self.output_file))

        # Verify content
        with open(self.output_file, 'r', encoding='utf-8') as f:
            written_data = json.load(f)

        self.assertEqual(written_data, test_items)

    def test_close_spider_json_formatting(self):
        """Test that JSON is properly formatted with indentation"""
        test_items = [
            {'title': 'Test Article', 'content': 'Test content with unicode: ñáéíóú'}
        ]

        self.pipeline.items = test_items
        self.pipeline.close_spider(self.mock_spider)

        # Read raw file content
        with open(self.output_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Verify indentation (indent=2)
        self.assertIn('  {', content)

        # Verify unicode characters are not escaped
        self.assertIn('ñáéíóú', content)

    def test_close_spider_empty_items(self):
        """Test that close_spider handles empty items list"""
        self.pipeline.items = []
        self.pipeline.close_spider(self.mock_spider)

        self.assertTrue(os.path.exists(self.output_file))

        with open(self.output_file, 'r', encoding='utf-8') as f:
            written_data = json.load(f)

        self.assertEqual(written_data, [])

    def test_close_spider_overwrites_existing_file(self):
        """Test that close_spider overwrites existing file"""
        # Create directory and initial file
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        with open(self.output_file, 'w') as f:
            json.dump([{'old': 'data'}], f)

        # Write new data
        new_items = [{'new': 'data'}]
        self.pipeline.items = new_items
        self.pipeline.close_spider(self.mock_spider)

        # Verify old data is replaced
        with open(self.output_file, 'r', encoding='utf-8') as f:
            written_data = json.load(f)

        self.assertEqual(written_data, new_items)


if __name__ == '__main__':
    unittest.main()
