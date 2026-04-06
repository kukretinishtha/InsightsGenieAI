#!/bin/bash

# InsightGenie AI Startup Script

set -e

echo "Starting InsightGenie AI Application..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3.12 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
cd backend
pip install -r requirements.txt -q
cd ..

# Start the application
echo "Starting FastAPI application on http://localhost:8000"
echo "API documentation available at http://localhost:8000/docs"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
