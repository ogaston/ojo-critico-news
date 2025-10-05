# News Debate Synthesis Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml first for dependency caching
COPY pyproject.toml ./

# Extract and install dependencies without the package itself
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    "ag2>=0.9.9" \
    "openai>=1.0.0" \
    "python-dotenv>=1.1.1" \
    "pymongo>=4.6.0" \
    "pydantic>=2.6.1" \
    "pydantic-settings>=2.0.0" \
    "structlog>=23.2.0" \
    "tenacity>=8.2.0"

# Copy all application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Default command
CMD ["python", "main.py"]
