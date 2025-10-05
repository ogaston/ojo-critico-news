# News Debate Synthesis AG2

AI-powered news credibility assessment using AG2 (AutoGen 2.0) framework with OpenAI GPT-4 Mini.

## 🎯 Overview

This system implements a formal adversarial evaluation methodology using 5 specialized AI agents that conduct structured debates to assess news article credibility. Built on AG2 framework for enhanced performance and reliability.

## 🤖 The Five AI Agents

1. **Moderator Agent** - Presents articles objectively and manages debate flow
2. **Proponent Agent** - Argues for article accuracy with evidence-based reasoning
3. **Opponent Agent** - Challenges article credibility through critical analysis
4. **Synthesis Agent** - Provides comprehensive evaluation reports
5. **Analysis Agent** - Performs quantitative graph analysis and probability scoring

## 📋 11-Step Structured Debate Process

### Phase 1: Presentation & Opening (Steps 1-3)
- Moderator: Neutral article presentation
- Proponent: Opening statement defending accuracy
- Opponent: Opening statement challenging accuracy

### Phase 2: Cross-Examination (Steps 4-5)
- Proponent: Cross-examines Opponent's challenges
- Opponent: Cross-examines Proponent's defenses

### Phase 3: Rebuttals (Steps 6-7)
- Proponent: Rebuttal defending against challenges
- Opponent: Rebuttal reinforcing skepticism

### Phase 4: Closing Arguments (Steps 8-9)
- Proponent: Final argument for accuracy
- Opponent: Final argument against accuracy

### Phase 5: Analysis & Synthesis (Steps 10-11)
- SynthesisAgent: Comprehensive evaluation report
- AnalysisAgent: Quantitative analysis and probability scoring

## 🚀 Key Features

- **AG2 Framework**: Latest AutoGen 2.0 for improved performance
- **GPT-4 Mini**: Cost-effective OpenAI model integration
- **MongoDB Integration**: Persistent article and synthesis storage
- **Batch Processing**: Handle multiple articles efficiently
- **Robust Error Handling**: Timeout protection and graceful degradation
- **Structured Output**: JSON-formatted analysis with probability scores
- **Bilingual Support**: Spanish translations for broader accessibility

## 📦 Installation

```bash
# Clone the repository
git clone <repository-url>
cd news-debate-synth

# Install dependencies
pip install -e .

# For development
pip install -e ".[dev]"
```

## ⚙️ Configuration

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key_here
MONGO_URI=mongodb://admin:admin123@localhost:27017/
MONGO_DB=news_db
LOG_LEVEL=INFO
```

## 🏃‍♂️ Usage

### Single Article Processing
```python
from news-debate-synth import DebateOrchestrator

orchestrator = DebateOrchestrator()
result = orchestrator.process_single_article()
```

### Batch Processing
```python
results = orchestrator.process_batch(batch_size=10)
```

### Command Line
```bash
# Process single article
python -m news-debate-synth --single

# Batch processing (default: 10 articles)
python -m news-debate-synth --batch 20
```

## 📊 Output Structure

### Synthesis Data
```json
{
  "report": "Comprehensive evaluation report...",
  "verdict": "True|Likely True|Unclear|Likely False|False"
}
```

### Analysis Data
```json
{
  "nodes": [...],
  "edges": [...],
  "pro_score": 0.75,
  "opp_score": 0.25,
  "prob_true": 0.72,
  "verdict": "Likely True",
  "rationale": "Analysis rationale..."
}
```

## 🐳 Docker Deployment

```bash
# Build image
docker build -t news-debate-synth .

# Run container
docker run -d --env-file .env news-debate-synth
```

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=news-debate-synth
```

## 📈 Performance

- **Cost Optimized**: GPT-4 Mini reduces API costs by ~60%
- **Improved Reliability**: AG2 framework enhancements
- **Scalable**: Batch processing with configurable concurrency
- **Monitoring**: Structured logging and health checks

## 🔄 Migration from AutoGen v1

This project migrates from the original AutoGen framework to AG2, providing:
- Better error handling and recovery
- Improved conversation management
- Enhanced performance and reliability
- Modern Python practices and typing

## 📝 License

MIT License - see LICENSE file for details.
