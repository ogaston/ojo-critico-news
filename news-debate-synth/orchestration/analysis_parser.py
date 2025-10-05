"""
Analysis parsing utilities for AG2 debate synthesis
"""
import json
from typing import Any, Dict
from config.logging import get_logger

logger = get_logger(__name__)


class AnalysisParser:
    """Parses and validates analysis output from AnalysisAgent"""
    
    def parse_analysis_json(self, analysis_msg: str) -> Dict[str, Any]:
        """
        Parse JSON from analysis message with robust error handling
        
        Args:
            analysis_msg: Raw analysis message from AnalysisAgent
            
        Returns:
            Parsed analysis data with fallbacks
        """
        try:
            # Try to find JSON in the message
            start_idx = analysis_msg.find('{')
            end_idx = analysis_msg.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = analysis_msg[start_idx:end_idx]
                parsed_data = json.loads(json_str)
                
                # Validate required fields
                validated_data = self._validate_analysis_data(parsed_data)
                logger.info("Successfully parsed analysis JSON")
                return validated_data
                
        except json.JSONDecodeError as e:
            logger.warning("Failed to parse analysis JSON", error=str(e))
        except Exception as e:
            logger.error("Unexpected error parsing analysis", error=str(e))
        
        # Fallback: return structured fallback data
        fallback_data = {
            'raw_analysis': analysis_msg,
            'nodes': [],
            'edges': [],
            'pro_score': 0.5,
            'opp_score': 0.5,
            'prob_true': 0.5,
            'verdict': 'parse_error',
            'rationale': 'Failed to parse analysis output'
        }
        
        logger.warning("Using analysis fallback data")
        return fallback_data
    
    def _validate_analysis_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize analysis data structure
        
        Args:
            data: Raw parsed JSON data
            
        Returns:
            Validated and normalized data
        """
        # Ensure required fields exist with defaults
        validated = {
            'nodes': data.get('nodes', []),
            'edges': data.get('edges', []),
            'pro_score': self._validate_score(data.get('pro_score', 0.5)),
            'opp_score': self._validate_score(data.get('opp_score', 0.5)),
            'prob_true': self._validate_probability(data.get('prob_true', 0.5)),
            'verdict': data.get('verdict', 'unknown'),
            'rationale': data.get('rationale', 'No rationale provided'),
            'raw_analysis': data.get('raw_analysis', '')
        }
        
        # Validate node structure
        validated['nodes'] = self._validate_nodes(validated['nodes'])
        
        # Validate edge structure
        validated['edges'] = self._validate_edges(validated['edges'])
        
        return validated
    
    def _validate_score(self, score: Any) -> float:
        """Validate and normalize score values"""
        try:
            score_float = float(score)
            return max(0.0, min(1.0, score_float))  # Clamp between 0 and 1
        except (ValueError, TypeError):
            return 0.5
    
    def _validate_probability(self, prob: Any) -> float:
        """Validate and normalize probability values"""
        try:
            prob_float = float(prob)
            return max(0.0, min(1.0, prob_float))  # Clamp between 0 and 1
        except (ValueError, TypeError):
            return 0.5
    
    def _validate_nodes(self, nodes: Any) -> list:
        """Validate node structure"""
        if not isinstance(nodes, list):
            return []
        
        validated_nodes = []
        for node in nodes:
            if isinstance(node, dict):
                validated_node = {
                    'id': str(node.get('id', '')),
                    'text': str(node.get('text', '')),
                    'role': str(node.get('role', 'unknown')),
                    'credibility_score': self._validate_score(node.get('credibility_score', 0.5)),
                    'specificity': self._validate_score(node.get('specificity', 0.5)),
                    'consistency': self._validate_score(node.get('consistency', 0.5)),
                    'weight': self._validate_score(node.get('weight', 1.0))
                }
                validated_nodes.append(validated_node)
        
        return validated_nodes
    
    def _validate_edges(self, edges: Any) -> list:
        """Validate edge structure"""
        if not isinstance(edges, list):
            return []
        
        validated_edges = []
        valid_relations = ['support', 'attack', 'refers']
        
        for edge in edges:
            if isinstance(edge, dict):
                relation = edge.get('relation', 'refers')
                if relation not in valid_relations:
                    relation = 'refers'
                
                validated_edge = {
                    'source': str(edge.get('source', '')),
                    'target': str(edge.get('target', '')),
                    'relation': relation
                }
                validated_edges.append(validated_edge)
        
        return validated_edges
