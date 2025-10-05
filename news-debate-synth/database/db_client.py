"""
MongoDB client for News Debate Synthesis AG2
"""
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from pymongo import MongoClient, ASCENDING
from bson.objectid import ObjectId

from config.settings import get_settings
from config.logging import get_logger
from database.models import ArticleModel, SynthesisModel, SynthesisReportModel, AnalysisReportModel

logger = get_logger(__name__)


class NewsDebateDB:
    """Enhanced MongoDB client for AG2 news debate synthesis"""

    def __init__(self, mongo_uri: Optional[str] = None, mongo_db: Optional[str] = None):
        settings = get_settings()
        self.mongo_uri = mongo_uri or settings.mongo_uri
        self.mongo_db = mongo_db or settings.mongo_db
        self.client: Optional[MongoClient] = None
        self.db = None
        self.articles_collection = None
        self.synthesis_collection = None

    def connect(self) -> None:
        """Initialize MongoDB connection with enhanced error handling"""
        try:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client[self.mongo_db]
            self.articles_collection = self.db['articles']
            self.synthesis_collection = self.db['synthesis']

            # Create indexes for better performance
            self._create_indexes()
            
            # Test connection
            self.client.admin.command('ping')
            logger.info("Connected to MongoDB", database=self.mongo_db)
            
        except Exception as e:
            logger.error("Failed to connect to MongoDB", error=str(e))
            raise

    def _create_indexes(self) -> None:
        """Create database indexes for optimal performance"""
        try:
            # Articles collection indexes
            self.articles_collection.create_index([('status', ASCENDING)])
            self.articles_collection.create_index([('scraped_at', ASCENDING)])
            self.articles_collection.create_index([('source', ASCENDING)])
            
            # Synthesis collection indexes
            self.synthesis_collection.create_index([('article_id', ASCENDING)])
            self.synthesis_collection.create_index([('created_at', ASCENDING)])
            self.synthesis_collection.create_index([('verdict', ASCENDING)])
            self.synthesis_collection.create_index([('probability_true', ASCENDING)])
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.warning("Failed to create some indexes", error=str(e))

    def close(self) -> None:
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

    def get_unprocessed_article(self) -> Optional[Dict[str, Any]]:
        """
        Get one article that hasn't been synthesized yet
        Returns: article document or None
        """
        try:
            article = self.articles_collection.find_one(
                {'$or': [
                    {'status': 'new'}, 
                    {'status': {'$exists': False}}
                ]},
                sort=[('scraped_at', ASCENDING)]
            )
            
            if article:
                # Mark as processing
                self.articles_collection.update_one(
                    {'_id': article['_id']},
                    {'$set': {
                        'status': 'processing', 
                        'processing_started_at': datetime.utcnow()
                    }}
                )
                logger.info("Retrieved unprocessed article", article_id=str(article['_id']))
                
            return article
            
        except Exception as e:
            logger.error("Failed to get unprocessed article", error=str(e))
            return None

    def get_unprocessed_articles_batch(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get multiple articles that haven't been synthesized yet
        Returns: list of article documents
        """
        try:
            articles = list(self.articles_collection.find(
                {'$or': [
                    {'status': 'new'}, 
                    {'status': {'$exists': False}}
                ]},
                sort=[('scraped_at', ASCENDING)]
            ).limit(limit))
            
            if articles:
                article_ids = [article['_id'] for article in articles]
                self.articles_collection.update_many(
                    {'_id': {'$in': article_ids}},
                    {'$set': {
                        'status': 'processing', 
                        'processing_started_at': datetime.utcnow()
                    }}
                )
                logger.info("Retrieved article batch", count=len(articles))
                
            return articles
            
        except Exception as e:
            logger.error("Failed to get article batch", error=str(e))
            return []

    def save_synthesis(
        self, 
        article_id: ObjectId, 
        synthesis_data: Dict[str, Any], 
        analysis_data: Dict[str, Any]
    ) -> Optional[ObjectId]:
        """
        Save synthesis results to MongoDB with enhanced validation
        """
        try:
            if isinstance(article_id, str):
                article_id = ObjectId(article_id)

            # Create synthesis document
            synthesis_doc = {
                'article_id': article_id,
                'synthesis_report': synthesis_data,
                'analysis_report': analysis_data,
                'created_at': datetime.utcnow(),
                'verdict': synthesis_data.get('verdict', 'unknown'),
                'probability_true': analysis_data.get('prob_true', 0.5)
            }

            result = self.synthesis_collection.insert_one(synthesis_doc)

            # Update article status
            self.articles_collection.update_one(
                {'_id': article_id},
                {'$set': {
                    'synthesis_id': result.inserted_id,
                    'status': 'completed',
                    'processing_completed_at': datetime.utcnow()
                }}
            )

            logger.info(
                "Synthesis saved successfully", 
                synthesis_id=str(result.inserted_id),
                article_id=str(article_id)
            )
            return result.inserted_id
            
        except Exception as e:
            logger.error("Failed to save synthesis", error=str(e), article_id=str(article_id))
            return None

    def mark_article_failed(self, article_id: ObjectId, error_message: Optional[str] = None) -> None:
        """Mark an article as failed processing"""
        try:
            if isinstance(article_id, str):
                article_id = ObjectId(article_id)
                
            update_data = {
                'status': 'failed',
                'processing_failed_at': datetime.utcnow()
            }
            
            if error_message:
                update_data['error_message'] = error_message
                
            self.articles_collection.update_one(
                {'_id': article_id},
                {'$set': update_data}
            )
            
            logger.warning("Article marked as failed", article_id=str(article_id), error=error_message)
            
        except Exception as e:
            logger.error("Failed to mark article as failed", error=str(e))

    def mark_articles_batch_failed(
        self, 
        article_ids: List[ObjectId], 
        error_message: Optional[str] = None
    ) -> None:
        """Mark multiple articles as failed processing"""
        try:
            if not article_ids:
                return
                
            # Convert string IDs to ObjectId if needed
            object_ids = []
            for article_id in article_ids:
                if isinstance(article_id, str):
                    object_ids.append(ObjectId(article_id))
                else:
                    object_ids.append(article_id)
                
            update_data = {
                'status': 'failed',
                'processing_failed_at': datetime.utcnow()
            }
            
            if error_message:
                update_data['error_message'] = error_message
                
            result = self.articles_collection.update_many(
                {'_id': {'$in': object_ids}},
                {'$set': update_data}
            )
            
            logger.warning(
                "Articles marked as failed", 
                count=result.modified_count, 
                error=error_message
            )
            
        except Exception as e:
            logger.error("Failed to mark articles as failed", error=str(e))

    def get_synthesis_by_article_id(self, article_id: ObjectId) -> Optional[Dict[str, Any]]:
        """Get synthesis for a specific article"""
        try:
            if isinstance(article_id, str):
                article_id = ObjectId(article_id)
            return self.synthesis_collection.find_one({'article_id': article_id})
        except Exception as e:
            logger.error("Failed to get synthesis", error=str(e))
            return None

    def get_article_with_synthesis(self, article_id: ObjectId) -> Dict[str, Any]:
        """Get article and its synthesis together"""
        try:
            if isinstance(article_id, str):
                article_id = ObjectId(article_id)

            article = self.articles_collection.find_one({'_id': article_id})
            synthesis = self.get_synthesis_by_article_id(article_id)

            return {
                'article': article,
                'synthesis': synthesis
            }
        except Exception as e:
            logger.error("Failed to get article with synthesis", error=str(e))
            return {'article': None, 'synthesis': None}

    def reset_processing_articles(self) -> int:
        """Reset articles stuck in processing state"""
        try:
            result = self.articles_collection.update_many(
                {'status': 'processing'},
                {'$set': {'status': 'new'}, '$unset': {'processing_started_at': 1}}
            )
            logger.info("Reset processing articles", count=result.modified_count)
            return result.modified_count
        except Exception as e:
            logger.error("Failed to reset processing articles", error=str(e))
            return 0

    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            total_articles = self.articles_collection.count_documents({})
            new_articles = self.articles_collection.count_documents({'status': 'new'})
            processing_articles = self.articles_collection.count_documents({'status': 'processing'})
            completed_articles = self.articles_collection.count_documents({'status': 'completed'})
            failed_articles = self.articles_collection.count_documents({'status': 'failed'})
            total_synthesis = self.synthesis_collection.count_documents({})
            
            return {
                'total_articles': total_articles,
                'new_articles': new_articles,
                'processing_articles': processing_articles,
                'completed_articles': completed_articles,
                'failed_articles': failed_articles,
                'total_synthesis': total_synthesis,
                'completion_rate': completed_articles / total_articles if total_articles > 0 else 0
            }
        except Exception as e:
            logger.error("Failed to get statistics", error=str(e))
            return {}
