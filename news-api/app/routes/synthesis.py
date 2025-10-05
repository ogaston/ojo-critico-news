from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.database import get_database
from app.models import (
    SynthesisResponse,
    SynthesisData,
    AnalysisData,
    ArticleWithSynthesis,
    ArticleResponse,
    PaginatedSynthesis
)
from app.config import settings
from bson import ObjectId

router = APIRouter()

def serialize_synthesis(synthesis: dict) -> SynthesisResponse:
    """
    Convert MongoDB synthesis document to SynthesisResponse
    """
    # Parse synthesis_report
    synthesis_report_data = synthesis.get("synthesis_report", {})
    synthesis_data = SynthesisData(
        report=synthesis_report_data.get("report", ""),
        verdict=synthesis_report_data.get("verdict", "unknown")
    )

    # Parse analysis_report
    analysis_report_data = synthesis.get("analysis_report", {})
    analysis_data = AnalysisData(
        nodes=analysis_report_data.get("nodes", []),
        edges=analysis_report_data.get("edges", []),
        pro_score=analysis_report_data.get("pro_score", 0.0),
        opp_score=analysis_report_data.get("opp_score", 0.0),
        prob_true=analysis_report_data.get("prob_true", 0.5),
        verdict=analysis_report_data.get("verdict", "unknown"),
        rationale=analysis_report_data.get("rationale", ""),
        raw_analysis=analysis_report_data.get("raw_analysis")
    )

    return SynthesisResponse(
        id=str(synthesis["_id"]),
        article_id=str(synthesis.get("article_id", "")),
        synthesis_report=synthesis_data,
        analysis_report=analysis_data,
        created_at=synthesis.get("created_at"),
        verdict=synthesis.get("verdict", "unknown"),
        probability_true=synthesis.get("probability_true", 0.5)
    )

def serialize_article(article: dict) -> ArticleResponse:
    """
    Convert MongoDB document to ArticleResponse
    """
    return ArticleResponse(
        id=str(article["_id"]),
        title=article.get("title", ""),
        short_description=article.get("short_description", ""),
        category=article.get("category", "undefined"),
        photo_url=article.get("photo_url", ""),
        content=article.get("content", ""),
        author=article.get("author", "unknown"),
        created_at=article.get("created_at", ""),
        url=article.get("url", ""),
        source=article.get("source", ""),
        scraped_at=article.get("scraped_at"),
        status=article.get("status", "new")
    )

@router.get("/synthesis", response_model=PaginatedSynthesis)
async def get_syntheses(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of syntheses per page"),
    verdict: Optional[str] = Query(None, description="Filter by verdict")
):
    """
    Get paginated list of debate syntheses
    """
    db = get_database()
    synthesis_collection = db['synthesis']

    # Build query filters
    filters = {}
    if verdict:
        filters["verdict"] = verdict

    # Get total count
    total = await synthesis_collection.count_documents(filters)

    # Get paginated results
    skip = (page - 1) * page_size
    cursor = synthesis_collection.find(filters).sort("created_at", -1).skip(skip).limit(page_size)

    syntheses = []
    async for synthesis in cursor:
        syntheses.append(serialize_synthesis(synthesis))

    return PaginatedSynthesis(
        total=total,
        page=page,
        page_size=page_size,
        syntheses=syntheses
    )

@router.get("/synthesis/{synthesis_id}", response_model=SynthesisResponse)
async def get_synthesis(synthesis_id: str):
    """
    Get a specific synthesis by ID
    """
    db = get_database()
    synthesis_collection = db['synthesis']

    # Validate ObjectId
    if not ObjectId.is_valid(synthesis_id):
        raise HTTPException(status_code=400, detail="Invalid synthesis ID format")

    synthesis = await synthesis_collection.find_one({"_id": ObjectId(synthesis_id)})

    if not synthesis:
        raise HTTPException(status_code=404, detail="Synthesis not found")

    return serialize_synthesis(synthesis)

@router.get("/synthesis/article/{article_id}", response_model=SynthesisResponse)
async def get_synthesis_by_article(article_id: str):
    """
    Get synthesis for a specific article
    """
    db = get_database()
    synthesis_collection = db['synthesis']

    # Validate ObjectId
    if not ObjectId.is_valid(article_id):
        raise HTTPException(status_code=400, detail="Invalid article ID format")

    synthesis = await synthesis_collection.find_one({"article_id": ObjectId(article_id)})

    if not synthesis:
        raise HTTPException(status_code=404, detail="Synthesis not found for this article")

    return serialize_synthesis(synthesis)

@router.get("/articles-with-synthesis", response_model=list[ArticleWithSynthesis])
async def get_articles_with_synthesis(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of articles per page"),
    source: Optional[str] = Query(None, description="Filter by news source"),
    category: Optional[str] = Query(None, description="Filter by category"),
    verdict: Optional[str] = Query(None, description="Filter by synthesis verdict"),
    only_completed: bool = Query(True, description="Only show articles with completed synthesis")
):
    """
    Get articles with their debate synthesis results
    This endpoint is perfect for displaying news with their debate results on the website
    """
    db = get_database()
    articles_collection = db[settings.MONGO_COLLECTION]
    synthesis_collection = db['synthesis']

    # Build query filters for articles
    filters = {}
    if source:
        filters["source"] = source
    if category:
        filters["category"] = category
    if only_completed:
        filters["status"] = "completed"

    # Get paginated articles
    skip = (page - 1) * page_size
    cursor = articles_collection.find(filters).sort("scraped_at", -1).skip(skip).limit(page_size)

    results = []
    async for article in cursor:
        article_response = serialize_article(article)

        # Get synthesis for this article
        synthesis_doc = None
        if article.get("synthesis_id"):
            synthesis_doc = await synthesis_collection.find_one({"_id": article["synthesis_id"]})
        else:
            # Try to find synthesis by article_id
            synthesis_doc = await synthesis_collection.find_one({"article_id": article["_id"]})

        synthesis_response = None
        if synthesis_doc:
            # Filter by verdict if specified
            if verdict and synthesis_doc.get("verdict") != verdict:
                continue
            synthesis_response = serialize_synthesis(synthesis_doc)
        elif verdict:
            # Skip if verdict filter is specified but no synthesis exists
            continue

        results.append(ArticleWithSynthesis(
            article=article_response,
            synthesis=synthesis_response
        ))

    return results

@router.get("/synthesis-stats")
async def get_synthesis_stats():
    """
    Get statistics about synthesis results
    """
    db = get_database()
    synthesis_collection = db['synthesis']

    total_syntheses = await synthesis_collection.count_documents({})

    # Get counts by verdict
    pipeline_verdict = [
        {"$group": {"_id": "$verdict", "count": {"$sum": 1}}}
    ]
    verdicts_stats = await synthesis_collection.aggregate(pipeline_verdict).to_list(length=None)

    # Get average probability_true
    pipeline_avg = [
        {"$group": {"_id": None, "avg_prob": {"$avg": "$probability_true"}}}
    ]
    avg_result = await synthesis_collection.aggregate(pipeline_avg).to_list(length=None)
    avg_probability = avg_result[0]["avg_prob"] if avg_result else 0.5

    return {
        "total_syntheses": total_syntheses,
        "by_verdict": {item["_id"]: item["count"] for item in verdicts_stats},
        "average_probability_true": avg_probability
    }
