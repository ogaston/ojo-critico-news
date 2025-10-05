from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    """
    Custom ObjectId type for Pydantic
    """
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")

class Article(BaseModel):
    """
    Article model representing a news article
    """
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    title: str
    short_description: Optional[str] = ""
    category: Optional[str] = "undefined"
    photo_url: Optional[str] = ""
    content: str
    author: Optional[str] = "unknown"
    created_at: str  # Date from the source
    url: str
    source: str
    scraped_at: Optional[datetime] = None
    status: Optional[str] = "new"

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class ArticleResponse(BaseModel):
    """
    Article response model for API responses
    """
    id: str
    title: str
    short_description: str
    category: str
    photo_url: str
    content: str
    author: str
    created_at: str
    url: str
    source: str
    scraped_at: Optional[datetime] = None
    status: str

class PaginatedArticles(BaseModel):
    """
    Paginated articles response
    """
    total: int
    page: int
    page_size: int
    articles: list[ArticleResponse]

# Synthesis/Debate Models

class SynthesisData(BaseModel):
    """
    Synthesis data from debate evaluation
    """
    report: str
    verdict: str  # True, Likely True, Unclear, Likely False, False

class AnalysisData(BaseModel):
    """
    Analysis data with debate graph and scores
    """
    nodes: Optional[List[Dict[str, Any]]] = []
    edges: Optional[List[Dict[str, Any]]] = []
    pro_score: Optional[float] = 0.0
    opp_score: Optional[float] = 0.0
    prob_true: Optional[float] = 0.5
    verdict: Optional[str] = "unknown"
    rationale: Optional[str] = ""
    raw_analysis: Optional[str] = None

class SynthesisResponse(BaseModel):
    """
    Synthesis response model
    """
    id: str
    article_id: str
    synthesis_report: SynthesisData
    analysis_report: AnalysisData
    created_at: datetime
    verdict: str
    probability_true: float

class ArticleWithSynthesis(BaseModel):
    """
    Article with its debate synthesis
    """
    article: ArticleResponse
    synthesis: Optional[SynthesisResponse] = None

class PaginatedSynthesis(BaseModel):
    """
    Paginated synthesis response
    """
    total: int
    page: int
    page_size: int
    syntheses: List[SynthesisResponse]
