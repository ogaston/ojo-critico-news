"""
Command-line interface for News Debate Synthesis AG2
"""
import sys
import argparse
from orchestration.debate_orchestrator import DebateOrchestrator
from config.logging import configure_logging, get_logger
from database.db_client import NewsDebateDB

# Configure logging
configure_logging()
logger = get_logger(__name__)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="News Debate Synthesis AG2 - AI-powered news credibility assessment"
    )
    
    parser.add_argument(
        "--single", 
        action="store_true",
        help="Process a single article (legacy mode)"
    )
    
    parser.add_argument(
        "--batch",
        type=int,
        default=10,
        help="Process articles in batch (default: 10)"
    )
    
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show database statistics"
    )
    
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset articles stuck in processing state"
    )
    
    args = parser.parse_args()
    
    try:
        if args.stats:
            show_statistics()
        elif args.reset:
            reset_processing_articles()
        elif args.single:
            process_single_article()
        else:
            process_batch(args.batch)
            
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error("Unexpected error", error=str(e))
        sys.exit(1)


def process_single_article():
    """Process a single article"""
    logger.info("Starting single article processing")
    
    orchestrator = DebateOrchestrator()
    result = orchestrator.process_single_article()
    
    if result:
        logger.info("Single article processing completed successfully")
        print(f"✅ Article processed successfully: {result['article_id']}")
    else:
        logger.warning("Single article processing failed")
        print("❌ No articles to process or processing failed")


def process_batch(batch_size: int):
    """Process articles in batch"""
    logger.info("Starting batch processing", batch_size=batch_size)
    
    orchestrator = DebateOrchestrator()
    results = orchestrator.process_batch(batch_size)
    
    # Print summary
    print(f"\n📊 Batch Processing Results:")
    print(f"   Total articles: {results['total']}")
    print(f"   Successfully processed: {results['processed']}")
    print(f"   Failed: {results['failed']}")
    print(f"   Success rate: {results.get('success_rate', 0):.1f}%")
    
    if results['failed'] > 0:
        print(f"\n❌ Failed articles:")
        for result in results['results']:
            if result['status'] == 'failed':
                print(f"   - {result['article_id']}: {result.get('error', 'Unknown error')}")


def show_statistics():
    """Show database statistics"""
    logger.info("Retrieving database statistics")
    
    db = NewsDebateDB()
    db.connect()
    
    try:
        stats = db.get_statistics()
        
        print(f"\n📈 Database Statistics:")
        print(f"   Total articles: {stats.get('total_articles', 0)}")
        print(f"   New articles: {stats.get('new_articles', 0)}")
        print(f"   Processing articles: {stats.get('processing_articles', 0)}")
        print(f"   Completed articles: {stats.get('completed_articles', 0)}")
        print(f"   Failed articles: {stats.get('failed_articles', 0)}")
        print(f"   Total synthesis: {stats.get('total_synthesis', 0)}")
        print(f"   Completion rate: {stats.get('completion_rate', 0):.1%}")
        
    finally:
        db.close()


def reset_processing_articles():
    """Reset articles stuck in processing state"""
    logger.info("Resetting processing articles")
    
    db = NewsDebateDB()
    db.connect()
    
    try:
        count = db.reset_processing_articles()
        print(f"✅ Reset {count} articles from processing to new status")
        
    finally:
        db.close()


if __name__ == "__main__":
    main()
