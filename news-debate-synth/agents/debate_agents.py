"""
Specialized debate agents for News Debate Synthesis AG2
"""
from typing import List
from autogen import AssistantAgent, UserProxyAgent

from config.settings import get_settings
from config.logging import get_logger
from agents.base_agent import BaseDebateAgent

logger = get_logger(__name__)


class ModeratorAgent(BaseDebateAgent):
    """Moderator agent that presents articles and manages debate flow"""
    
    def __init__(self):
        system_message = (
            "Role: Debate moderator. Start the debate immediately when asked.\n"
            "Present the news article clearly and then call on Proponent for opening statement.\n"
            "Keep your initial presentation concise (under 100 words) and focus on the news content.\n"
            "After presenting, say: 'Proponent, please give your opening statement arguing this news is accurate.'\n"
            "Do not manage the entire debate flow - just start it properly.\n"
            "IMPORTANT: Once the AnalysisAgent provides the final analysis, the debate is complete. Do not continue. TERMINATE THE DEBATE IMMEDIATELY."
        )
        super().__init__("Moderator", system_message)


class ProponentAgent(BaseDebateAgent):
    """Agent that argues for news article accuracy"""
    
    def __init__(self):
        settings = get_settings()
        system_message = (
            "Role: Argue that the news article is TRUE and ACCURATE.\n"
            "You must defend the credibility of the specific facts, dates, names, quotes, and events mentioned in the news.\n"
            "Focus on verifiable elements that support the news accuracy.\n"
            f"Keep responses concise (≤{settings.max_words_per_message} words per message).\n"
            "Analyze specific claims made in the news article.\n"
            "Question dates, names, events, quotes mentioned.\n"
            "Evaluate the credibility of sources and statements.\n"
            "Cite or hypothesize concrete checks (dates, actors, numbers, quotes).\n"
            "Explicitly mark references you rely on (even if hypothetical) like: [Ref: outlet/title].\n"
            "Do NOT fabricate facts; when uncertain, say so.\n"
        )
        super().__init__("Proponent", system_message)


class OpponentAgent(BaseDebateAgent):
    """Agent that challenges news article accuracy"""
    
    def __init__(self):
        settings = get_settings()
        system_message = (
            "Role: Argue that the news article is FALSE or INACCURATE.\n"
            "You must challenge the credibility of the specific facts, dates, names, quotes, and events mentioned in the news.\n"
            "Focus on inconsistencies, missing information, or questionable elements that cast doubt on the news accuracy.\n"
            f"Keep responses concise (≤{settings.max_words_per_message} words per message).\n"
            "Challenge specific claims, dates, statistics.\n"
            "Question source reliability and potential bias.\n"
            "Identify logical fallacies or unsupported leaps.\n"
            "Point out missing information gaps.\n"
            "Cite or hypothesize concrete checks (dates, actors, numbers, quotes).\n"
            "Explicitly mark references you rely on (even if hypothetical) like: [Ref: outlet/title].\n"
            "Do NOT fabricate facts; when uncertain, say so.\n"
        )
        super().__init__("Opponent", system_message)


class SynthesisAgent(BaseDebateAgent):
    """Agent that provides comprehensive evaluation reports"""
    
    def __init__(self):
        system_message = (
            "Role: Summarize the debate with critical analysis.\n"
            "Produce an EVALUATION REPORT with sections:\n"
            "- Verifiability (specific, checkable details?)\n"
            "- Sources (reputable citations or outlets?)\n"
            "- Tone/Style (objective vs. emotive?)\n"
            "- Corroboration (consistent across independent sources?)\n"
            "- Key Points from Proponent / Opponent\n"
            "- Weaknesses / Gaps (both sides)\n"
            "- Preliminary Verdict (True / Likely True / Unclear / Likely False / False) + 1-2 sentence rationale.\n"
            "IMPORTANT: Do not add any title or subtitle to the report just the content I mentioned."
            "The information outputted should be in spanish."
        )
        super().__init__("SynthesisAgent", system_message)


class AnalysisAgent(BaseDebateAgent):
    """Agent that performs quantitative graph analysis"""
    
    def __init__(self):
        settings = get_settings()
        spanish_instruction = ""
        if settings.enable_spanish_translation:
            spanish_instruction = "Translate the debate log to Spanish.\n"
            
        system_message = (
            f"Role: Build a role-aware debate graph from the debate log. {spanish_instruction}"
            "Steps:\n"
            "1) Extract atomic propositions from each message (max 5 per message). Tag each with role.\n"
            "2) Build edges: support/attack/refers based on explicit mentions or contradictions.\n"
            "3) Score node credibility heuristically using: specificity, consistency, concessions, and being unrefuted.\n"
            "4) Weight roles: Opening<Rebuttal<Closing (1.0/1.1/1.2).\n"
            "5) Aggregate to a probability that the claim is TRUE.\n"
            "Return JSON: {nodes:[...], edges:[...], pro_score, opp_score, prob_true, verdict, rationale}.\n"
            "The information outputted should be in spanish."
            "IMPORTANT: After providing your analysis, the debate is complete. Do not continue the conversation."
        )
        super().__init__("AnalysisAgent", system_message)


class DebateAgentFactory:
    """Factory class for creating debate agents"""
    
    @staticmethod
    def create_all_agents() -> List[AssistantAgent]:
        """Create all debate agents and return their AG2 instances"""
        moderator = ModeratorAgent()
        proponent = ProponentAgent()
        opponent = OpponentAgent()
        synthesis = SynthesisAgent()
        analysis = AnalysisAgent()
        
        agents = [
            moderator.get_agent(),
            proponent.get_agent(),
            opponent.get_agent(),
            synthesis.get_agent(),
            analysis.get_agent()
        ]
        
        logger.info("Created all debate agents", count=len(agents))
        return agents
    
    @staticmethod
    def create_user_proxy() -> UserProxyAgent:
        """Create user proxy agent for debate initiation"""
        return UserProxyAgent(name="User", human_input_mode="NEVER")
