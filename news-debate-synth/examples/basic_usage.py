"""
Basic usage examples for News Debate Synthesis AG2
"""
import asyncio
from news-debate-synth import DebateOrchestrator
from news-debate-synth.config.logging import configure_logging, get_logger

# Configure logging
configure_logging()
logger = get_logger(__name__)


def example_single_article():
    """Example: Process a single article"""
    print("🔍 Processing single article...")
    
    orchestrator = DebateOrchestrator()
    result = orchestrator.process_single_article()
    
    if result:
        print(f"✅ Article processed: {result['article_id']}")
        print(f"📊 Verdict: {result['synthesis']['verdict']}")
        print(f"🎯 Probability True: {result['analysis']['prob_true']:.2f}")
    else:
        print("❌ No articles to process")


def example_batch_processing():
    """Example: Process multiple articles in batch"""
    print("📦 Processing article batch...")
    
    orchestrator = DebateOrchestrator()
    results = orchestrator.process_batch(batch_size=5)
    
    print(f"📊 Batch Results:")
    print(f"   Total: {results['total']}")
    print(f"   Processed: {results['processed']}")
    print(f"   Failed: {results['failed']}")
    print(f"   Success Rate: {results.get('success_rate', 0):.1f}%")


def example_custom_article():
    """Example: Process a custom article (not from database)"""
    print("📝 Processing custom article...")
    
    # Custom article data
    custom_article = {
        '_id': 'custom_001',
        'title': 'Breaking: New AI Technology Announced',
        'content': 'A major tech company announced today a breakthrough in artificial intelligence...',
        'source': 'TechNews',
        'url': 'https://example.com/ai-breakthrough'
    }
    
    orchestrator = DebateOrchestrator()
    result = orchestrator.process_single_article(custom_article)
    
    if result:
        print(f"✅ Custom article processed")
        print(f"📊 Synthesis Report: {result['synthesis']['report'][:100]}...")
        print(f"🎯 Analysis Verdict: {result['analysis']['verdict']}")


def main():
    """Run all examples"""
    print("🚀 News Debate Synthesis AG2 - Usage Examples\n")
    
    try:
        # Example 1: Single article
        example_single_article()
        print("\n" + "="*50 + "\n")
        
        # Example 2: Batch processing
        example_batch_processing()
        print("\n" + "="*50 + "\n")
        
        # Example 3: Custom article
        example_custom_article()
        
    except Exception as e:
        logger.error("Example execution failed", error=str(e))
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
