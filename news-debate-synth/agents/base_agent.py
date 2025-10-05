"""
Base agent configuration for News Debate Synthesis AG2
"""
from typing import Optional
from autogen import AssistantAgent
from autogen.oai import OpenAIWrapper

from config.settings import get_settings
from config.logging import get_logger

logger = get_logger(__name__)


class BaseDebateAgent:
    """Base class for all debate agents with common configuration"""
    
    def __init__(self, name: str, system_message: str, model_override: Optional[str] = None):
        self.settings = get_settings()
        self.name = name
        self.system_message = system_message
        
        # Create LLM config for AG2/AutoGen
        self.llm_config = {
            "model": model_override or self.settings.openai_model,
            "api_key": self.settings.openai_api_key,
            "temperature": 0.7,
        }
        
        # Create AG2 agent
        self.agent = AssistantAgent(
            name=self.name,
            llm_config=self.llm_config,
            system_message=self.system_message,
        )
        
        logger.info("Created debate agent", name=self.name, model=self.settings.openai_model)
    
    def get_agent(self) -> AssistantAgent:
        """Get the underlying AG2 agent"""
        return self.agent
