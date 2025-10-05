# News API

FastAPI application for serving news articles collected from Dominican news sources.

## Features

- **RESTful API** for accessing news articles
- **MongoDB integration** using Motor (async driver)
- **Pagination support** for efficient data retrieval
- **Filtering** by source, category, and status
- **Statistics endpoint** for analytics
- **Docker support** for easy deployment

## Project Structure

```
news-api/
├── app/
│   ├── routes/
│   │   ├── __init__.py
│   │   └── articles.py       # Article endpoints
│   ├── __init__.py
│   ├── config.py              # Configuration settings
│   ├── database.py            # MongoDB connection
│   └── models.py              # Pydantic models
├── main.py                    # FastAPI application entry point
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## API Endpoints

### Articles

- `GET /api/v1/articles` - Get paginated list of articles
  - Query parameters:
    - `page` (default: 1) - Page number
    - `page_size` (default: 10, max: 100) - Articles per page
    - `source` (optional) - Filter by news source
    - `category` (optional) - Filter by category
    - `status` (optional) - Filter by status

- `GET /api/v1/articles/{article_id}` - Get specific article by ID

- `GET /api/v1/sources` - Get list of all available news sources

- `GET /api/v1/categories` - Get list of all available categories

- `GET /api/v1/stats` - Get statistics about articles collection

### Health

- `GET /` - Root endpoint with API information
- `GET /health` - Health check endpoint

## Installation

### Prerequisites

- Python 3.11+
- MongoDB instance (can use the one from docker-compose.yaml in the project root)

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file from example:
```bash
cp .env.example .env
```

3. Update `.env` with your MongoDB configuration

### Running Locally

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

API documentation will be available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Docker Deployment

### Build the image:
```bash
docker build -t news-api .
```

### Run the container:
```bash
docker run -d \
  -p 8000:8000 \
  -e MONGO_URI=mongodb://admin:admin123@mongodb:27017/ \
  -e MONGO_DB=news_db \
  --name news-api \
  news-api
```

## Integration with news_collector

This API serves the data collected by the `news_collector` scraper. The `news_collector` stores articles in MongoDB using the `MongoDBPipeline`, and this API reads from the same database to serve the data.

### Article Schema

Articles are stored with the following fields:

- `title` - Article title
- `short_description` - Brief description
- `category` - Article category
- `photo_url` - URL to article image
- `content` - Full article content
- `author` - Article author
- `created_at` - Publication date from source
- `url` - Original article URL
- `source` - News source (e.g., "listin_diario", "el_nacional")
- `scraped_at` - Timestamp when article was scraped
- `status` - Processing status (default: "new")

## Development

### Adding New Endpoints

1. Create new route files in `app/routes/`
2. Import and include the router in `main.py`

### Adding New Models

1. Define Pydantic models in `app/models.py`
2. Use models in route handlers for request/response validation

## Environment Variables

- `MONGO_URI` - MongoDB connection URI
- `MONGO_DB` - MongoDB database name
- `API_TITLE` - API title
- `API_VERSION` - API version

## License

MIT
