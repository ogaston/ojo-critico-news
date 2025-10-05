"""
Main debate orchestrator for News Debate Synthesis AG2
"""
import json
import signal
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from autogen import GroupChat, GroupChatManager

from agents.debate_agents import DebateAgentFactory
from database.db_client import NewsDebateDB
from config.settings import get_settings
from config.logging import get_logger
# from orchestration.termination import DebateTerminationHandler  # Temporarily disabled
from orchestration.analysis_parser import AnalysisParser

logger = get_logger(__name__)


class TimeoutException(Exception):
    """Exception raised when debate times out"""
    pass


@contextmanager
def timeout(seconds: int):
    """Context manager for handling timeouts"""
    def signal_handler(signum, frame):
        raise TimeoutException(f"Timed out after {seconds} seconds")
    
    old_handler = signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    
    try:
        yield
    finally:
        signal.signal(signal.SIGALRM, old_handler)
        signal.alarm(0)


class DebateOrchestrator:
    """Main orchestrator for AG2 debate synthesis"""
    
    def __init__(self):
        self.settings = get_settings()
        self.db = NewsDebateDB()
        # self.termination_handler = DebateTerminationHandler()  # Temporarily disabled
        self.analysis_parser = AnalysisParser()
        
        # Create agents
        self.agents = DebateAgentFactory.create_all_agents()
        self.user_proxy = DebateAgentFactory.create_user_proxy()
        
        logger.info("Debate orchestrator initialized")
    
    def process_single_article(self, article: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Process a single article through the debate pipeline
        
        Args:
            article: Optional article dict. If None, fetches from database
            
        Returns:
            Result dict with synthesis data or None if failed
        """
        # Connect to database
        self.db.connect()
        
        try:
            # Get article from database if not provided
            if article is None:
                article = self.db.get_unprocessed_article()
                if not article:
                    logger.info("No unprocessed articles found")
                    return None
            
            article_id = article['_id']
            news_title = article.get('title', 'Untitled')
            news_text = article.get('content', '')
            news_source = article.get('source', 'unknown')
            news_url = article.get('url', '')
            
            logger.info(
                "Processing article",
                article_id=str(article_id),
                source=news_source,
                title=news_title[:100]
            )
            
            # Run the debate
            result = self._run_debate_session(article_id, news_title, news_text, news_source, news_url)
            
            if result:
                logger.info("Article processed successfully", article_id=str(article_id))
                return result
            else:
                logger.error("Article processing failed", article_id=str(article_id))
                self.db.mark_article_failed(article_id, "Debate processing failed")
                return None
                
        except Exception as e:
            logger.error("Error processing article", error=str(e))
            if 'article_id' in locals():
                self.db.mark_article_failed(article_id, str(e))
            return None
        finally:
            self.db.close()
    
    def process_batch(self, batch_size: Optional[int] = None) -> Dict[str, Any]:
        """
        Process multiple articles in batch
        
        Args:
            batch_size: Number of articles to process. Uses settings default if None
            
        Returns:
            Batch processing results
        """
        batch_size = batch_size or self.settings.batch_size
        logger.info("Starting batch processing", batch_size=batch_size)
        
        # Connect to database
        self.db.connect()
        
        try:
            # Get batch of articles
            articles = self.db.get_unprocessed_articles_batch(batch_size)
            
            if not articles:
                logger.info("No unprocessed articles found for batch")
                return {
                    'processed': 0,
                    'failed': 0,
                    'total': 0,
                    'results': []
                }
            
            logger.info("Processing article batch", count=len(articles))
            
            # Process each article
            processed_count = 0
            failed_count = 0
            failed_article_ids = []
            results = []
            
            for i, article in enumerate(articles, 1):
                article_id = article['_id']
                news_title = article.get('title', 'Untitled')
                news_source = article.get('source', 'unknown')
                
                logger.info(
                    "Processing batch article",
                    progress=f"{i}/{len(articles)}",
                    article_id=str(article_id),
                    source=news_source
                )
                
                try:
                    result = self._run_single_debate_session(article)
                    
                    if result:
                        processed_count += 1
                        results.append({
                            'article_id': str(article_id),
                            'status': 'completed',
                            'title': news_title,
                            'source': news_source
                        })
                        logger.info("Batch article completed", article_id=str(article_id))
                    else:
                        failed_count += 1
                        failed_article_ids.append(article_id)
                        results.append({
                            'article_id': str(article_id),
                            'status': 'failed',
                            'title': news_title,
                            'source': news_source,
                            'error': 'Processing returned None'
                        })
                        logger.warning("Batch article failed", article_id=str(article_id))
                        
                except Exception as e:
                    failed_count += 1
                    failed_article_ids.append(article_id)
                    error_msg = str(e)
                    results.append({
                        'article_id': str(article_id),
                        'status': 'failed',
                        'title': news_title,
                        'source': news_source,
                        'error': error_msg
                    })
                    logger.error("Batch article error", article_id=str(article_id), error=error_msg)
            
            # Mark failed articles
            if failed_article_ids:
                self.db.mark_articles_batch_failed(failed_article_ids, "Batch processing failed")
            
            # Summary
            total_articles = len(articles)
            success_rate = (processed_count / total_articles) * 100 if total_articles > 0 else 0
            
            logger.info(
                "Batch processing completed",
                total=total_articles,
                processed=processed_count,
                failed=failed_count,
                success_rate=f"{success_rate:.1f}%"
            )
            
            return {
                'processed': processed_count,
                'failed': failed_count,
                'total': total_articles,
                'success_rate': success_rate,
                'results': results
            }
            
        finally:
            self.db.close()
    
    def _run_single_debate_session(self, article: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Run debate session for a single article (used in batch processing)"""
        article_id = article['_id']
        news_title = article.get('title', 'Untitled')
        news_text = article.get('content', '')
        news_source = article.get('source', 'unknown')
        news_url = article.get('url', '')
        
        return self._run_debate_session(article_id, news_title, news_text, news_source, news_url)
    
    def _run_debate_session(
        self, 
        article_id: str, 
        news_title: str, 
        news_text: str, 
        news_source: str, 
        news_url: str
    ) -> Optional[Dict[str, Any]]:
        """
        Run the complete debate session for an article
        
        Returns:
            Result dict with synthesis data or None if failed
        """
        # Create seed message
        seed = (
            f"SEED: \n NEWS TITLE: {news_title}\n\nNEWS TEXT:\n{news_text}\n\n"
            "We will conduct a structured debate on whether this news is accurate."
        )
        
        # Create termination condition function
        def is_termination_msg(message):
            """Check if the debate should terminate"""
            if not message:
                return False
            
            content = str(message.get("content", "")).lower()
            sender = message.get("name", "")
            
            # Terminate if AnalysisAgent has provided final analysis
            if sender == "AnalysisAgent":
                if any(indicator in content for indicator in ["json", "analysis", "verdict", "prob_true"]):
                    return True
            
            # Terminate if we see completion indicators
            completion_indicators = [
                "analysis report", "final analysis", "verdict:", 
                "prob_true", "preliminary verdict"
            ]
            if any(indicator in content for indicator in completion_indicators):
                return True
            
            return False
        
        # Create GroupChat with proper termination condition
        gc = GroupChat(
            agents=self.agents,
            messages=[],
            max_round=self.settings.max_rounds,
            allow_repeat_speaker=False,
            # is_termination_msg=is_termination_msg
        )
        
        # Create GroupChatManager with LLM config
        mgr = GroupChatManager(
            groupchat=gc,
            llm_config={
                "model": self.settings.openai_model,
                "api_key": self.settings.openai_api_key,
                "temperature": 0.7,
            },
            system_message="IMPORTANT: Once the AnalysisAgent has provided its final analysis, the debate is over. TERMINATE THE DEBATE IMMEDIATELY."
        )
        
        # Create debate instructions
        debate_instructions = self._create_debate_instructions(
            news_title, news_source, news_text
        )
        
        # Run the debate with timeout protection
        synth_msg = ""
        analysis_msg = ""
        
        try:
            with timeout(self.settings.max_debate_timeout):
                result = self.user_proxy.initiate_chat(
                    mgr,
                    message=debate_instructions,
                    max_turns=1
                )
                
        except TimeoutException as e:
            logger.warning("Debate timed out", article_id=str(article_id), error=str(e))
        except Exception as e:
            logger.error("Debate session error", article_id=str(article_id), error=str(e))
        
        # Extract synthesis and analysis from messages
        synth_msg, analysis_msg = self._extract_final_messages(gc.messages)
        
        # Use fallbacks if messages are missing
        if not synth_msg:
            synth_msg = "Synthesis not completed - debate ended early"
            logger.warning("Using synthesis fallback", article_id=str(article_id))
        
        if not analysis_msg:
            analysis_msg = json.dumps({
                "raw_analysis": "Analysis not completed - debate ended early",
                "prob_true": 0.5,
                "verdict": "incomplete"
            })
            logger.warning("Using analysis fallback", article_id=str(article_id))
        
        # Parse results
        synthesis_data = {
            'report': synth_msg,
            'verdict': self._extract_verdict(synth_msg)
        }
        
        analysis_data = self.analysis_parser.parse_analysis_json(analysis_msg)
        
        # Save to database
        try:
            synthesis_id = self.db.save_synthesis(article_id, synthesis_data, analysis_data)
            if synthesis_id:
                return {
                    'article_id': article_id,
                    'synthesis_id': synthesis_id,
                    'synthesis': synthesis_data,
                    'analysis': analysis_data
                }
            else:
                return None
                
        except Exception as e:
            logger.error("Failed to save synthesis", article_id=str(article_id), error=str(e))
            return None
    
    def _create_debate_instructions(self, news_title: str, news_source: str, news_text: str) -> str:
        """Create structured debate instructions"""
        return f"""
We will now conduct a structured debate about this news article's accuracy. Follow this exact order and make sure each agent speaks in their respective role and step:

1. Moderator: Present the news and explain the debate format
2. Proponent: Opening statement (argue the news is TRUE and ACCURATE)
3. Opponent: Opening statement (argue the news is FALSE or INACCURATE)  
4. Proponent: Cross-examine the Opponent
5. Opponent: Cross-examine the Proponent
6. Proponent: Rebuttal defending the news accuracy
7. Opponent: Rebuttal challenging the news accuracy
8. Proponent: Closing statement on why the news is accurate
9. Opponent: Closing statement on why the news is inaccurate
10. SynthesisAgent: Provide EVALUATION REPORT (in spanish)
11. AnalysisAgent: Provide final ANALYSIS REPORT (in spanish)

Each agent should speak only once per step. Keep responses concise (≤{self.settings.max_words_per_message} words).

NEWS TO DEBATE:
Title: {news_title}
Source: {news_source}
Content: {news_text}

Begin the debate now.

NOTE: Once the AnalysisAgent has provided its final analysis, the debate is over.
"""
    
    def _extract_final_messages(self, messages: List[Dict[str, Any]]) -> Tuple[str, str]:
        """Extract synthesis and analysis messages from conversation"""
        synth_msg = ""
        analysis_msg = ""
        
        for msg in messages:
            speaker = msg.get("name", "Unknown")
            if speaker == "SynthesisAgent":
                synth_msg = msg["content"]
            elif speaker == "AnalysisAgent":
                analysis_msg = msg["content"]
        
        return synth_msg, analysis_msg
    
    def _extract_verdict(self, synth_msg: str) -> str:
        """Extract verdict from synthesis message"""
        verdicts = ['True', 'Likely True', 'Unclear', 'Likely False', 'False']
        for verdict in verdicts:
            if verdict.lower() in synth_msg.lower():
                return verdict
        return 'Unknown'
