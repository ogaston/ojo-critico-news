# Ojo Crítico Newsroom

A Next.js 14 application styled with Tailwind CSS that consumes the FastAPI service in ../news-api to present Dominican news articles alongside their AI-generated debate synthesis.

## Features
- Washington Post inspired monochrome layout with strong typography
- Home page that lists the latest articles from the FastAPI /api/v1/articles endpoint
- Detail page for each article with source metadata, image, and full content
- Debate synthesis sidebar that surfaces verdict, probability, and report text from the FastAPI backend
- Graceful empty states and loading skeletons for a newsroom feel

## System Architecture

This frontend is part of a complete news analysis pipeline:

1. **news-collector** - Scrapy spiders scrape articles from Dominican newspapers and store them in MongoDB
2. **news-debate-synth** - AutoGen AI agents debate article credibility and generate synthesis reports
3. **news-api** - FastAPI backend serves articles and synthesis from MongoDB
4. **news-website** - Next.js frontend displays articles with AI analysis

## Getting Started

### Prerequisites
- The entire stack should be running via Docker Compose (see root README)
- MongoDB should be populated with articles from news-collector
- news-api should be accessible at http://localhost:8000

### Local Development

1. Install dependencies:
```bash
npm install
```

2. Set environment variables (create `.env.local`):
```bash
NEWS_API_BASE_URL=http://localhost:8000/api/v1
```

3. Run the development server:
```bash
npm run dev
```

4. Visit http://localhost:3000 to view the newsroom.

## API Endpoints Used

The app consumes these FastAPI endpoints:

- `GET /api/v1/articles` - Paginated articles list with query params (page, page_size, source, category, status)
- `GET /api/v1/articles/{id}` - Single article details
- `GET /api/v1/synthesis/{article_id}` - AI debate synthesis for an article
- `GET /api/v1/sources` - Available news sources
- `GET /api/v1/categories` - Available categories

The synthesis sidebar automatically fetches synthesis data and renders a waiting state when no synthesis is available yet.

## Project Structure
- app/page.tsx � Newsroom landing page
- app/articles/[id]/page.tsx � Article detail with synthesis sidebar
- app/globals.css � Tailwind layer definitions and custom styles
- components/article-card.tsx � Card variations used in the feed
- components/article-list.tsx � Home page article layout orchestration
- components/site-header.tsx � Washington Post inspired masthead
- components/synthesis-panel.tsx � Debate synthesis verdict component
- lib/api.ts � API client with FastAPI plus synthesis fallbacks
- lib/format.ts � Date and text utility helpers
- types/index.ts � Shared TypeScript interfaces

## Styling Notes
- Typography relies on Playfair Display for headlines and Source Sans 3 for body copy, loaded through next/font
- Tailwind custom theme colors (ink, parchment, accent) evoke a minimal newspaper palette
- Components emphasize generous whitespace, uppercase accents, and subtle borders to mirror investigative broadsheets

## Data Flow

1. **Article Collection**: Scrapy spiders collect articles every 12 hours → MongoDB `articles` collection (status: `new`)
2. **Synthesis Processing**: AutoGen debate system processes new articles → MongoDB `synthesis` collection
3. **API Serving**: FastAPI serves articles and synthesis with cross-references
4. **Frontend Display**: Next.js fetches and displays articles with AI analysis sidebar

## MongoDB Collections

### Articles Collection
Articles stored with bidirectional reference to synthesis:
- Basic fields: title, content, source, url, author, category, photo_url
- Status tracking: `new` → `processing` → `completed` or `failed`
- References: `synthesis_id` (links to synthesis collection)

### Synthesis Collection
AI debate analysis results:
- `article_id`: Reference to original article
- `synthesis_report`: Verdict and analysis
- `analysis_report`: Debate graph, scores, probability
- `verdict`: True | Likely True | Unclear | Likely False | False
- `probability_true`: 0.0 - 1.0

## Running with Docker

The entire stack runs with Docker Compose from the root directory:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f news-website

# Stop all services
docker-compose down
```

Services available:
- **news-website**: http://localhost:3000
- **news-api**: http://localhost:8000 (docs at /docs)
- **mongo-express**: http://localhost:8081 (MongoDB GUI)

## Next Steps
- Add pagination and filtering controls (source, category) to the home page
- Add search functionality across articles
- Wire end-to-end tests that validate the data contract between FastAPI and Next.js when CI tooling is ready
