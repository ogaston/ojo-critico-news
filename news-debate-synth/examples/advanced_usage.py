"""
Advanced usage examples for News Debate Synthesis AG2
"""
from news-debate-synth.database.db_client import NewsDebateDB
from news-debate-synth.orchestration.debate_orchestrator import DebateOrchestrator
from news-debate-synth.config.settings import get_settings
from news-debate-synth.config.logging import configure_logging, get_logger

# Configure logging
configure_logging()
logger = get_logger(__name__)


def example_database_operations():
    """Example: Direct database operations"""
    print("🗄️ Database Operations Example...")
    
    db = NewsDebateDB()
    db.connect()
    
    try:
        # Get statistics
        stats = db.get_statistics()
        print(f"📊 Database Statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # Reset processing articles if any are stuck
        reset_count = db.reset_processing_articles()
        if reset_count > 0:
            print(f"🔄 Reset {reset_count} stuck articles")
        
        # Get a sample article
        article = db.get_unprocessed_article()
        if article:
            print(f"📰 Sample article: {article.get('title', 'No title')[:50]}...")
        else:
            print("📰 No unprocessed articles found")
            
    finally:
        db.close()


def example_configuration():
    """Example: Working with configuration"""
    print("⚙️ Configuration Example...")
    
    settings = get_settings()
    
    print(f"🤖 OpenAI Model: {settings.openai_model}")
    print(f"🗄️ MongoDB Database: {settings.mongo_db}")
    print(f"⏱️ Max Debate Timeout: {settings.max_debate_timeout}s")
    print(f"📦 Default Batch Size: {settings.batch_size}")
    print(f"💬 Max Words per Message: {settings.max_words_per_message}")
    print(f"🌍 Spanish Translation: {settings.enable_spanish_translation}")


def example_error_handling():
    """Example: Error handling and recovery"""
    print("🛡️ Error Handling Example...")
    
    orchestrator = DebateOrchestrator()
    
    try:
        # Attempt to process with potential timeout
        result = orchestrator.process_single_article()
        
        if result:
            print("✅ Processing completed successfully")
        else:
            print("⚠️ Processing completed but no result returned")
            
    except Exception as e:
        logger.error("Processing failed with error", error=str(e))
        print(f"❌ Error occurred: {e}")
        print("🔄 System will attempt recovery on next run")


def example_analysis_parsing():
    """Example: Working with analysis data"""
    print("📊 Analysis Parsing Example...")
    
    from news-debate-synth.orchestration.analysis_parser import AnalysisParser
    
    parser = AnalysisParser()
    
    # Sample analysis message (what AnalysisAgent might return)
    sample_analysis = '''
    Based on the debate, here's my analysis:
    {
        "nodes": [
            {"id": "n1", "text": "Company announced breakthrough", "role": "proponent", "credibility_score": 0.8},
            {"id": "n2", "text": "No independent verification", "role": "opponent", "credibility_score": 0.6}
        ],
        "edges": [
            {"source": "n2", "target": "n1", "relation": "attack"}
        ],
        "pro_score": 0.7,
        "opp_score": 0.6,
        "prob_true": 0.65,
        "verdict": "Likely True",
        "rationale": "Strong evidence but lacks independent verification"
    }
    '''
    
    parsed = parser.parse_analysis_json(sample_analysis)
    
    print(f"🎯 Verdict: {parsed['verdict']}")
    print(f"📈 Probability True: {parsed['prob_true']}")
    print(f"🔗 Nodes: {len(parsed['nodes'])}")
    print(f"➡️ Edges: {len(parsed['edges'])}")
    print(f"💭 Rationale: {parsed['rationale']}")


def example_monitoring():
    """Example: System monitoring and health checks"""
    print("🔍 System Monitoring Example...")
    
    db = NewsDebateDB()
    
    try:
        db.connect()
        print("✅ Database connection: OK")
        
        # Check for stuck articles
        stats = db.get_statistics()
        processing_count = stats.get('processing_articles', 0)
        
        if processing_count > 0:
            print(f"⚠️ Warning: {processing_count} articles stuck in processing")
        else:
            print("✅ No stuck articles")
        
        # Check completion rate
        completion_rate = stats.get('completion_rate', 0)
        if completion_rate < 0.8:
            print(f"⚠️ Warning: Low completion rate ({completion_rate:.1%})")
        else:
            print(f"✅ Good completion rate ({completion_rate:.1%})")
            
    except Exception as e:
        print(f"❌ Database health check failed: {e}")
    finally:
        db.close()


def main():
    """Run all advanced examples"""
    print("🚀 News Debate Synthesis AG2 - Advanced Examples\n")
    
    examples = [
        example_database_operations,
        example_configuration,
        example_error_handling,
        example_analysis_parsing,
        example_monitoring
    ]
    
    for i, example in enumerate(examples, 1):
        try:
            example()
            if i < len(examples):
                print("\n" + "="*50 + "\n")
        except Exception as e:
            logger.error("Example failed", example=example.__name__, error=str(e))
            print(f"❌ {example.__name__} failed: {e}")


if __name__ == "__main__":
    main()
