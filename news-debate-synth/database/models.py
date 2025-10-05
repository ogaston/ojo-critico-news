"""
Database models for News Debate Synthesis AG2
Simplified version using dictionaries to avoid Pydantic v2 ObjectId issues
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

# For now, we'll use simple type aliases and handle validation in the database layer
# This avoids Pydantic v2 ObjectId compatibility issues
ArticleModel = Dict[str, Any]
SynthesisReportModel = Dict[str, Any]
AnalysisNodeModel = Dict[str, Any]
AnalysisEdgeModel = Dict[str, Any]
AnalysisReportModel = Dict[str, Any]
SynthesisModel = Dict[str, Any]
DebateMessageModel = Dict[str, Any]
DebateSessionModel = Dict[str, Any]
