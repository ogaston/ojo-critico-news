#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all module imports"""
    try:
        print("Testing config imports...")
        from config.settings import get_settings
        from config.logging import configure_logging, get_logger
        print("OK Config imports successful")
        
        print("Testing database imports...")
        from database.db_client import NewsDebateDB
        from database.models import ArticleModel
        print("OK Database imports successful")
        
        print("Testing agents imports...")
        from agents.base_agent import BaseDebateAgent
        from agents.debate_agents import DebateAgentFactory
        print("OK Agents imports successful")
        
        print("Testing orchestration imports...")
        from orchestration.analysis_parser import AnalysisParser
        from orchestration.termination import DebateTerminationHandler
        from orchestration.debate_orchestrator import DebateOrchestrator
        print("OK Orchestration imports successful")
        
        print("\nAll imports successful!")
        return True
        
    except ImportError as e:
        print(f"Import error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
