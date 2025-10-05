# News Collector - Unit Tests

This directory contains unit tests for the news_collector project, focusing on non-scraping functionality.

## Test Coverage

The test suite covers the following components:

### 1. **MongoDBPipeline** (`tests/test_pipelines.py`)
- Pipeline initialization and configuration
- MongoDB connection management (open/close spider)
- Item processing and storage
- Duplicate detection handling
- Error handling

### 2. **CustomJsonPipeline** (`tests/test_run_spider.py`)
- Pipeline initialization
- JSON file writing with proper formatting
- Directory creation
- Unicode handling
- Multiple items processing

### 3. **ArticleItem** (`tests/test_items.py`)
- Item field validation
- Field value setting and retrieval
- Dictionary conversion
- Unicode content handling
- Partial field population

## Running Tests

### Install Test Dependencies

```bash
pip install -r requirements-dev.txt
```

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_pipelines.py
pytest tests/test_run_spider.py
pytest tests/test_items.py
```

### Run with Coverage Report

```bash
pytest --cov=. --cov-report=html
```

This will generate an HTML coverage report in `htmlcov/index.html`.

### Run Specific Test

```bash
pytest tests/test_pipelines.py::TestMongoDBPipeline::test_process_item_success
```

## Test Structure

Each test file follows this structure:

- **setUp()**: Initialize test fixtures before each test
- **tearDown()**: Clean up after each test (if needed)
- **test_***: Individual test methods

## Mocking

Tests use Python's `unittest.mock` to mock external dependencies:
- MongoDB connections are mocked to avoid requiring a real database
- File system operations use temporary directories
- Spider loggers are mocked

## Notes

- Web scraping functionality is **not** tested as requested
- All tests are isolated and don't require external services
- Tests use temporary directories that are automatically cleaned up
