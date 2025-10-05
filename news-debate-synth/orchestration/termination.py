"""
Termination handling for AG2 debate sessions
"""
from typing import Any, Dict, List, Callable
from config.logging import get_logger

logger = get_logger(__name__)


class DebateTerminationHandler:
    """Handles termination conditions for debate sessions"""
    
    def __init__(self):
        self.completion_indicators = [
            "analysis report",
            "final analysis", 
            "verdict:",
            "prob_true",
            "preliminary verdict"
        ]
    
    def create_termination_condition(self) -> Callable[[Dict[str, Any]], bool]:
        """
        Create a termination condition function for GroupChat
        
        Returns:
            Function that determines if debate should terminate
        """
        def is_termination_msg(message: Dict[str, Any]) -> bool:
            """
            Termination condition for the debate.
            Returns True if the debate should terminate.
            """
            if not message:
                return False
            
            content = message.get("content", "").lower()
            sender = message.get("name", "")
            
            # Terminate if we've received analysis (usually the last step)
            if sender == "AnalysisAgent":
                if any(indicator in content for indicator in ["json", "analysis", "verdict"]):
                    logger.info("Terminating debate: AnalysisAgent completed")
                    return True
            
            # Terminate if we see completion indicators
            if any(indicator in content for indicator in self.completion_indicators):
                logger.info("Terminating debate: completion indicator found", indicator=True)
                return True
            
            return False
        
        return is_termination_msg
    
    def is_debate_complete(self, messages: List[Dict[str, Any]]) -> bool:
        """Check if debate has synthesis and analysis messages"""
        has_synthesis = any(msg.get("name") == "SynthesisAgent" for msg in messages)
        has_analysis = any(msg.get("name") == "AnalysisAgent" for msg in messages)
        
        is_complete = has_synthesis and has_analysis
        logger.info("Checking debate completion", has_synthesis=has_synthesis, has_analysis=has_analysis, complete=is_complete)
        
        return is_complete
