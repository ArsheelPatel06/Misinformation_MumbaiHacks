#!/bin/bash
# Start the DeepCheck MH API server

echo "🚀 Starting DeepCheck MH API Server..."
echo "========================================"
echo ""
echo "Server will start at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd "/Users/arsheelpatel/Desktop/DeepCheck MH"
python3 -m uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
