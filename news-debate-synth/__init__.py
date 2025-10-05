"""
News Debate Synthesis AG2
AI-powered news credibility assessment using AG2 framework
"""

from .orchestration.debate_orchestrator import DebateOrchestrator
from .config.settings import Settings

__version__ = "0.1.0"
__all__ = ["DebateOrchestrator", "Settings"]
