"""
Main entry point for News Debate Synthesis
"""
import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from orchestration.debate_orchestrator import DebateOrchestrator
from config.logging import configure_logging, get_logger

# Configure logging
configure_logging()
logger = get_logger(__name__)


def main():
    """Main function for running debate synthesis"""
    logger.info("Starting News Debate Synthesis")
    
    try:
        orchestrator = DebateOrchestrator()
        
        # Default to batch processing
        results = orchestrator.process_batch()
        
        logger.info(
            "Batch processing completed",
            processed=results['processed'],
            failed=results['failed'],
            total=results['total']
        )
        
        return results
        
    except Exception as e:
        logger.error("Main execution failed", error=str(e))
        raise


if __name__ == "__main__":
    main()
