"""
Tests for DebateOrchestrator
"""
import pytest
from unittest.mock import Mock, patch
from news-debate-synth.orchestration.debate_orchestrator import DebateOrchestrator


class TestDebateOrchestrator:
    """Test cases for DebateOrchestrator"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.orchestrator = DebateOrchestrator()
    
    def test_orchestrator_initialization(self):
        """Test orchestrator initializes correctly"""
        assert self.orchestrator is not None
        assert self.orchestrator.settings is not None
        assert len(self.orchestrator.agents) == 5
        assert self.orchestrator.user_proxy is not None
    
    @patch('news-debate-synth.orchestration.debate_orchestrator.NewsDebateDB')
    def test_process_single_article_no_articles(self, mock_db_class):
        """Test processing when no articles are available"""
        mock_db = Mock()
        mock_db.get_unprocessed_article.return_value = None
        mock_db_class.return_value = mock_db
        
        result = self.orchestrator.process_single_article()
        
        assert result is None
        mock_db.connect.assert_called_once()
        mock_db.close.assert_called_once()
    
    def test_extract_verdict(self):
        """Test verdict extraction from synthesis message"""
        test_cases = [
            ("The news is likely true based on evidence", "Likely True"),
            ("This appears to be false information", "False"),
            ("The verdict is unclear due to conflicting sources", "Unclear"),
            ("No clear verdict indicators", "Unknown")
        ]
        
        for message, expected in test_cases:
            result = self.orchestrator._extract_verdict(message)
            assert result == expected
    
    def test_create_debate_instructions(self):
        """Test debate instructions creation"""
        title = "Test News Title"
        source = "Test Source"
        content = "Test news content"
        
        instructions = self.orchestrator._create_debate_instructions(title, source, content)
        
        assert title in instructions
        assert source in instructions
        assert content in instructions
        assert "11-step" in instructions or "11 steps" in instructions.lower()
        assert "Moderator:" in instructions
        assert "AnalysisAgent:" in instructions
    
    def test_extract_final_messages(self):
        """Test extraction of synthesis and analysis messages"""
        messages = [
            {"name": "Moderator", "content": "Starting debate"},
            {"name": "SynthesisAgent", "content": "This is the synthesis report"},
            {"name": "AnalysisAgent", "content": "This is the analysis report"},
            {"name": "Proponent", "content": "Some argument"}
        ]
        
        synth_msg, analysis_msg = self.orchestrator._extract_final_messages(messages)
        
        assert synth_msg == "This is the synthesis report"
        assert analysis_msg == "This is the analysis report"
    
    def test_extract_final_messages_missing(self):
        """Test extraction when messages are missing"""
        messages = [
            {"name": "Moderator", "content": "Starting debate"},
            {"name": "Proponent", "content": "Some argument"}
        ]
        
        synth_msg, analysis_msg = self.orchestrator._extract_final_messages(messages)
        
        assert synth_msg == ""
        assert analysis_msg == ""
