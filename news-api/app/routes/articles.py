from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.database import get_database
from app.models import ArticleResponse, PaginatedArticles
from app.config import settings
from bson import ObjectId

router = APIRouter()

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

@router.get("/articles", response_model=PaginatedArticles)
async def get_articles(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of articles per page"),
    source: Optional[str] = Query(None, description="Filter by news source"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status")
):
    """
    Get paginated list of articles with optional filters
    """
    db = get_database()
    collection = db[settings.MONGO_COLLECTION]

    # Build query filters
    filters = {}
    if source:
        filters["source"] = source
    if category:
        filters["category"] = category
    if status:
        filters["status"] = status

    # Get total count
    total = await collection.count_documents(filters)

    # Get paginated results
    skip = (page - 1) * page_size
    cursor = collection.find(filters).sort("scraped_at", -1).skip(skip).limit(page_size)

    articles = []
    async for article in cursor:
        articles.append(serialize_article(article))

    return PaginatedArticles(
        total=total,
        page=page,
        page_size=page_size,
        articles=articles
    )

@router.get("/articles/{article_id}", response_model=ArticleResponse)
async def get_article(article_id: str):
    """
    Get a specific article by ID
    """
    db = get_database()
    collection = db[settings.MONGO_COLLECTION]

    # Validate ObjectId
    if not ObjectId.is_valid(article_id):
        raise HTTPException(status_code=400, detail="Invalid article ID format")

    article = await collection.find_one({"_id": ObjectId(article_id)})

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    return serialize_article(article)

@router.get("/sources")
async def get_sources():
    """
    Get list of all available news sources
    """
    db = get_database()
    collection = db[settings.MONGO_COLLECTION]

    sources = await collection.distinct("source")
    return {"sources": sources}

@router.get("/categories")
async def get_categories():
    """
    Get list of all available categories
    """
    db = get_database()
    collection = db[settings.MONGO_COLLECTION]

    categories = await collection.distinct("category")
    return {"categories": categories}

@router.get("/stats")
async def get_stats():
    """
    Get statistics about the articles collection
    """
    db = get_database()
    collection = db[settings.MONGO_COLLECTION]

    total_articles = await collection.count_documents({})

    # Get counts by source
    pipeline_source = [
        {"$group": {"_id": "$source", "count": {"$sum": 1}}}
    ]
    sources_stats = await collection.aggregate(pipeline_source).to_list(length=None)

    # Get counts by category
    pipeline_category = [
        {"$group": {"_id": "$category", "count": {"$sum": 1}}}
    ]
    categories_stats = await collection.aggregate(pipeline_category).to_list(length=None)

    return {
        "total_articles": total_articles,
        "by_source": {item["_id"]: item["count"] for item in sources_stats},
        "by_category": {item["_id"]: item["count"] for item in categories_stats}
    }
