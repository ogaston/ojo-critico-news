"""
Tests for AnalysisParser
"""
import pytest
import json
from news-debate-synth.orchestration.analysis_parser import AnalysisParser


class TestAnalysisParser:
    """Test cases for AnalysisParser"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.parser = AnalysisParser()
    
    def test_parse_valid_json(self):
        """Test parsing valid JSON analysis"""
        valid_json = '''
        Here's my analysis:
        {
            "nodes": [{"id": "n1", "text": "test", "role": "proponent", "credibility_score": 0.8}],
            "edges": [{"source": "n1", "target": "n2", "relation": "support"}],
            "pro_score": 0.7,
            "opp_score": 0.3,
            "prob_true": 0.75,
            "verdict": "Likely True",
            "rationale": "Strong evidence"
        }
        Additional text after JSON.
        '''
        
        result = self.parser.parse_analysis_json(valid_json)
        
        assert result['prob_true'] == 0.75
        assert result['verdict'] == "Likely True"
        assert result['rationale'] == "Strong evidence"
        assert len(result['nodes']) == 1
        assert len(result['edges']) == 1
    
    def test_parse_invalid_json(self):
        """Test parsing invalid JSON falls back gracefully"""
        invalid_json = "This is not JSON at all"
        
        result = self.parser.parse_analysis_json(invalid_json)
        
        assert result['verdict'] == 'parse_error'
        assert result['prob_true'] == 0.5
        assert result['raw_analysis'] == invalid_json
        assert result['nodes'] == []
        assert result['edges'] == []
    
    def test_parse_malformed_json(self):
        """Test parsing malformed JSON"""
        malformed_json = '{"nodes": [}, "prob_true": 0.8'  # Missing closing brace
        
        result = self.parser.parse_analysis_json(malformed_json)
        
        assert result['verdict'] == 'parse_error'
        assert result['prob_true'] == 0.5
    
    def test_validate_score_valid(self):
        """Test score validation with valid values"""
        assert self.parser._validate_score(0.5) == 0.5
        assert self.parser._validate_score(0.0) == 0.0
        assert self.parser._validate_score(1.0) == 1.0
    
    def test_validate_score_clamping(self):
        """Test score validation clamps out-of-range values"""
        assert self.parser._validate_score(-0.5) == 0.0
        assert self.parser._validate_score(1.5) == 1.0
    
    def test_validate_score_invalid_type(self):
        """Test score validation with invalid types"""
        assert self.parser._validate_score("invalid") == 0.5
        assert self.parser._validate_score(None) == 0.5
        assert self.parser._validate_score([]) == 0.5
    
    def test_validate_probability(self):
        """Test probability validation"""
        assert self.parser._validate_probability(0.75) == 0.75
        assert self.parser._validate_probability(-0.1) == 0.0
        assert self.parser._validate_probability(1.1) == 1.0
        assert self.parser._validate_probability("invalid") == 0.5
    
    def test_validate_nodes_valid(self):
        """Test node validation with valid data"""
        nodes = [
            {
                "id": "n1",
                "text": "Test node",
                "role": "proponent",
                "credibility_score": 0.8,
                "specificity": 0.7,
                "consistency": 0.9,
                "weight": 1.0
            }
        ]
        
        result = self.parser._validate_nodes(nodes)
        
        assert len(result) == 1
        assert result[0]['id'] == "n1"
        assert result[0]['credibility_score'] == 0.8
    
    def test_validate_nodes_missing_fields(self):
        """Test node validation with missing fields"""
        nodes = [{"id": "n1"}]  # Missing most fields
        
        result = self.parser._validate_nodes(nodes)
        
        assert len(result) == 1
        assert result[0]['id'] == "n1"
        assert result[0]['text'] == ""
        assert result[0]['role'] == "unknown"
        assert result[0]['credibility_score'] == 0.5
    
    def test_validate_nodes_invalid_type(self):
        """Test node validation with invalid input type"""
        result = self.parser._validate_nodes("not a list")
        assert result == []
        
        result = self.parser._validate_nodes(None)
        assert result == []
    
    def test_validate_edges_valid(self):
        """Test edge validation with valid data"""
        edges = [
            {"source": "n1", "target": "n2", "relation": "support"},
            {"source": "n2", "target": "n3", "relation": "attack"}
        ]
        
        result = self.parser._validate_edges(edges)
        
        assert len(result) == 2
        assert result[0]['relation'] == "support"
        assert result[1]['relation'] == "attack"
    
    def test_validate_edges_invalid_relation(self):
        """Test edge validation with invalid relation"""
        edges = [{"source": "n1", "target": "n2", "relation": "invalid_relation"}]
        
        result = self.parser._validate_edges(edges)
        
        assert len(result) == 1
        assert result[0]['relation'] == "refers"  # Default fallback
    
    def test_validate_analysis_data_complete(self):
        """Test complete analysis data validation"""
        data = {
            "nodes": [{"id": "n1", "text": "test", "role": "proponent", "credibility_score": 0.8}],
            "edges": [{"source": "n1", "target": "n2", "relation": "support"}],
            "pro_score": 0.7,
            "opp_score": 0.3,
            "prob_true": 0.75,
            "verdict": "Likely True",
            "rationale": "Good evidence"
        }
        
        result = self.parser._validate_analysis_data(data)
        
        assert result['prob_true'] == 0.75
        assert result['verdict'] == "Likely True"
        assert len(result['nodes']) == 1
        assert len(result['edges']) == 1
