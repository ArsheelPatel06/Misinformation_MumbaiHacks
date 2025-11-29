# DeepCheck MH - Misinformation Detection AI Agent

An AI-powered system for detecting, verifying, and explaining misinformation during global crises, with **advanced deepfake detection** for images and videos.

## 🎯 Main Features

### 1. **Deepfake Detection** (Primary Feature)
- **Dual-AI Verification**: Uses both Gemini Vision and OpenAI Vision APIs
- **Image Analysis**: Detects AI-generated and manipulated images
- **Video Analysis**: Frame-by-frame deepfake detection with temporal consistency checks
- **Metadata Analysis**: Examines EXIF data for manipulation signs
- **Consensus Mode**: Cross-validates results from both AI models for maximum accuracy
- **Detailed Reports**: Identifies specific artifacts and provides technical explanations

### 2. **Text Claim Verification**

- **Multi-Source Monitoring**: Aggregates content from RSS feeds, NewsAPI, and Reddit
- **Dual-AI Verification**: Uses both OpenAI GPT and Google Gemini for enhanced accuracy
- **Consensus Mode**: Cross-validates high-urgency claims using both AI models
- **Multi-Audience Explanations**: Generates explanations for simple, general, and expert audiences
- **Crisis Detection**: Automatically identifies claims related to pandemics, conflicts, climate events, etc.
- **REST API**: Full-featured API for integration with frontends

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add:
- `GEMINI_API_KEY` - Your Google Gemini API key
- `OPENAI_API_KEY` - Your OpenAI API key
- `NEWS_API_KEY` - (Optional) Your NewsAPI key

### 3. Run the API Server

```bash
python -m uvicorn src.api:app --reload
```

The API will be available at `http://localhost:8000`

### 4. API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation

## API Endpoints

### Text Claim Verification
- `GET /api/claims` - List all detected claims
- `GET /api/claims/{id}` - Get detailed claim information
- `GET /api/trending` - Get trending misinformation
- `POST /api/verify` - Verify a custom claim
- `POST /api/run-cycle` - Manually trigger detection cycle
- `GET /api/stats` - Get system statistics

### Deepfake Detection
- `POST /api/deepfake/upload` - Upload image or video for analysis
- `POST /api/deepfake/analyze/{media_id}` - Start deepfake analysis
- `GET /api/deepfake/results/{media_id}` - Get analysis results
- `GET /api/deepfake/results` - List all deepfake analyses

## Usage Example

### Verify a Custom Claim

```bash
curl -X POST "http://localhost:8000/api/verify" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Drinking hot water prevents COVID-19",
    "audience_level": "general"
  }'
```

### Get Trending Claims

```bash
curl "http://localhost:8000/api/trending?limit=10"
```

## Architecture

```
Content Sources → Content Monitor → Claim Extractor → Fact Checker → Explanation Generator → Database
                                         ↓                  ↓                   ↓
                                    Gemini API        OpenAI API          Multi-Audience
                                                      (Consensus)          Explanations
```

## Project Structure

```
DeepCheck MH/
├── src/
│   ├── config.py              # Configuration management
│   ├── database.py            # Database models
│   ├── models.py              # API models
│   ├── content_monitor.py     # Content aggregation
│   ├── claim_extractor.py     # AI claim extraction
│   ├── fact_checker.py        # Verification system
│   ├── explanation_generator.py # Explanation generation
│   ├── agent.py               # Main orchestrator
│   └── api.py                 # FastAPI server
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
└── README.md                 # This file
```

## Development

### Run Detection Cycle Manually

```python
from src.agent import agent
import asyncio

# Run a single detection cycle
stats = asyncio.run(agent.run_detection_cycle())
print(stats)
```

### Start Continuous Monitoring

```python
from src.agent import agent
import asyncio

# Start background monitoring
asyncio.run(agent.start_monitoring())
```

## License

MIT License
# Misinformation_MumbaiHacks
