"""
Unit tests for ArticleItem
"""
import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from spiders.items import ArticleItem


class TestArticleItem(unittest.TestCase):
    """Test cases for ArticleItem"""

    def test_item_creation(self):
        """Test creating an ArticleItem"""
        item = ArticleItem()

        self.assertIsInstance(item, ArticleItem)

    def test_item_fields_exist(self):
        """Test that all expected fields exist"""
        item = ArticleItem()

        expected_fields = [
            'title',
            'short_description',
            'category',
            'photo_url',
            'content',
            'author',
            'created_at',
            'url',
            'source'
        ]

        for field in expected_fields:
            self.assertIn(field, item.fields)

    def test_set_and_get_field_values(self):
        """Test setting and getting field values"""
        item = ArticleItem()

        item['title'] = 'Test Article Title'
        item['short_description'] = 'A short description'
        item['category'] = 'Technology'
        item['photo_url'] = 'https://example.com/photo.jpg'
        item['content'] = 'Full article content here'
        item['author'] = 'John Doe'
        item['created_at'] = '2024-01-01'
        item['url'] = 'https://example.com/article'
        item['source'] = 'test_source'

        self.assertEqual(item['title'], 'Test Article Title')
        self.assertEqual(item['short_description'], 'A short description')
        self.assertEqual(item['category'], 'Technology')
        self.assertEqual(item['photo_url'], 'https://example.com/photo.jpg')
        self.assertEqual(item['content'], 'Full article content here')
        self.assertEqual(item['author'], 'John Doe')
        self.assertEqual(item['created_at'], '2024-01-01')
        self.assertEqual(item['url'], 'https://example.com/article')
        self.assertEqual(item['source'], 'test_source')

    def test_item_to_dict(self):
        """Test converting item to dictionary"""
        item = ArticleItem()

        item['title'] = 'Test Title'
        item['content'] = 'Test Content'
        item['url'] = 'https://example.com/test'
        item['source'] = 'test_source'

        item_dict = dict(item)

        self.assertIsInstance(item_dict, dict)
        self.assertEqual(item_dict['title'], 'Test Title')
        self.assertEqual(item_dict['content'], 'Test Content')
        self.assertEqual(item_dict['url'], 'https://example.com/test')
        self.assertEqual(item_dict['source'], 'test_source')

    def test_item_partial_fields(self):
        """Test that item can be created with only some fields populated"""
        item = ArticleItem()

        item['title'] = 'Partial Article'
        item['url'] = 'https://example.com/partial'

        self.assertEqual(item['title'], 'Partial Article')
        self.assertEqual(item['url'], 'https://example.com/partial')

        # Other fields should not be set
        with self.assertRaises(KeyError):
            _ = item['content']

    def test_item_unicode_content(self):
        """Test that item handles unicode content correctly"""
        item = ArticleItem()

        item['title'] = 'Artículo con ñ y acentos'
        item['content'] = 'Contenido en español: ¿Qué tal? ¡Excelente!'
        item['author'] = 'José García'

        self.assertEqual(item['title'], 'Artículo con ñ y acentos')
        self.assertEqual(item['content'], 'Contenido en español: ¿Qué tal? ¡Excelente!')
        self.assertEqual(item['author'], 'José García')

    def test_item_empty_values(self):
        """Test that item can store empty values"""
        item = ArticleItem()

        item['title'] = ''
        item['content'] = None

        self.assertEqual(item['title'], '')
        self.assertIsNone(item['content'])

    def test_item_overwrite_field(self):
        """Test that field values can be overwritten"""
        item = ArticleItem()

        item['title'] = 'Original Title'
        self.assertEqual(item['title'], 'Original Title')

        item['title'] = 'Updated Title'
        self.assertEqual(item['title'], 'Updated Title')


if __name__ == '__main__':
    unittest.main()
