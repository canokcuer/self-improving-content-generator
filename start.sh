#!/bin/bash
# Start both servers for TheLifeCo Content Assistant

echo "Starting TheLifeCo Content Assistant..."
echo ""

# Start API server in background
echo "1. Starting API server on port 8000..."
python -m uvicorn content_assistant.api.main:app --port 8000 &
API_PID=$!

# Wait a moment for API to start
sleep 2

# Start Streamlit
echo "2. Starting Streamlit on port 8501..."
echo ""
echo "================================"
echo "App running at: http://localhost:8501"
echo "API running at: http://localhost:8000"
echo "Press Ctrl+C to stop both servers"
echo "================================"
echo ""

streamlit run content_assistant/app.py

# When Streamlit stops, also stop API
kill $API_PID 2>/dev/null
