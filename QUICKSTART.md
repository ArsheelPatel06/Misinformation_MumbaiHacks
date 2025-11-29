# Quick Start Guide

## 1. Setup Environment

First, create your `.env` file with your API keys:

```bash
cd "/Users/arsheelpatel/Desktop/DeepCheck MH"
cp .env.example .env
```

Then edit `.env` and add your API keys:
- Get Gemini API key from: https://makersuite.google.com/app/apikey
- Get OpenAI API key from: https://platform.openai.com/api-keys
- (Optional) Get NewsAPI key from: https://newsapi.org/

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## 3. Test the Setup

Run the test script to verify everything is configured correctly:

```bash
python test_setup.py
```

This will:
- Check if API keys are configured
- Test claim verification with both AI models
- Test content monitoring from RSS feeds

## 4. Start the API Server

```bash
python -m uvicorn src.api:app --reload
```

The API will be available at: http://localhost:8000

## 5. Try the API

### View API Documentation
Open in browser: http://localhost:8000/docs

### Run a Detection Cycle
```bash
curl -X POST "http://localhost:8000/api/run-cycle"
```

### Verify a Custom Claim
```bash
curl -X POST "http://localhost:8000/api/verify" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "5G towers spread coronavirus",
    "audience_level": "general"
  }'
```

### Get Trending Claims
```bash
curl "http://localhost:8000/api/trending"
```

### Get All Claims
```bash
curl "http://localhost:8000/api/claims"
```

## Next Steps

Once the backend is working, you can:
1. Build a frontend dashboard (React/Vite)
2. Add real-time WebSocket updates
3. Implement user authentication
4. Deploy to production

## Troubleshooting

### "API key not configured" error
- Make sure you created `.env` file (not `.env.example`)
- Check that API keys are properly set without quotes
- Restart the server after changing `.env`

### "No content items found"
- This is normal if RSS feeds are temporarily unavailable
- Try running the detection cycle again
- Check your internet connection

### Import errors
- Make sure you're in the project directory
- Run: `pip install -r requirements.txt` again
- Check Python version (requires 3.8+)
