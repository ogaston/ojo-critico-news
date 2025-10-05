#!/usr/bin/env python3
"""
Runner script for both Listín Diario and El Nacional spiders
"""

import os
import sys
import json
import logging
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Add current directory and spiders directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
spiders_dir = os.path.join(current_dir, 'spiders')
sys.path.append(current_dir)
sys.path.append(spiders_dir)

from spiders.listin_diario import ListinDiarioSpider
from spiders.el_nacional import ElNacionalSpider


class CustomJsonPipeline:
    """Custom pipeline to write properly formatted JSON"""
    
    def __init__(self, output_file):
        self.output_file = output_file
        self.items = []
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            output_file=crawler.settings.get('OUTPUT_FILE')
        )
    
    def open_spider(self, spider):
        self.items = []
    
    def process_item(self, item, spider):
        self.items.append(dict(item))
        return item
    
    def close_spider(self, spider):
        # Ensure outputs directory exists
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        
        # Write properly formatted JSON
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.items, f, ensure_ascii=False, indent=2)
        
        print(f"Spider {spider.name} completed! Output saved to: {self.output_file}")


def run_spiders():
    """Run both Listín Diario and El Nacional spiders"""

    # Configure logging to reduce verbosity
    logging.getLogger('pymongo').setLevel(logging.WARNING)
    logging.getLogger('pymongo.topology').setLevel(logging.WARNING)
    logging.getLogger('pymongo.connection').setLevel(logging.WARNING)
    logging.getLogger('pymongo.heartbeat').setLevel(logging.WARNING)

    # Configure Scrapy settings
    settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'ROBOTSTXT_OBEY': True,
        'DOWNLOAD_DELAY': 1,  # Be respectful to the server
        'RANDOMIZE_DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS': 16,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 8,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 60,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
        'ITEM_PIPELINES': {
            'pipelines.MongoDBPipeline': 100,  # MongoDB first
            'run_spider.CustomJsonPipeline': 300,  # JSON backup
        }
    }
    
    # Create a single CrawlerProcess
    process = CrawlerProcess(settings)
    
    # Add both spiders to the same process
    print("Starting Listín Diario spider...")
    process.crawl(ListinDiarioSpider, output_file='outputs/listin_diario_articles.json')
    
    print("Starting El Nacional spider...")
    process.crawl(ElNacionalSpider, output_file='outputs/el_nacional_articles.json')
    
    # Start the process (this will run both spiders)
    process.start()
    
    print("Both spiders completed!")


if __name__ == '__main__':
    run_spiders()