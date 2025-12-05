#!/bin/bash
set -e

echo "Starting Ollama LLM API..."

# If OLLAMA_BASE_URL is not set, try to start Ollama locally
if [ -z "$OLLAMA_BASE_URL" ]; then
    echo "OLLAMA_BASE_URL not set. Checking for local Ollama installation..."
    
    if command -v ollama &> /dev/null; then
        echo "Starting Ollama service..."
        ollama serve &
        OLLAMA_PID=$!
        
        # Wait for Ollama to start
        sleep 5
        
        # Pull the default model if not already present
        MODEL=${DEFAULT_MODEL:-ministral-3:8b-cloud}
        echo "Checking/pulling model: $MODEL"
        ollama pull $MODEL
        
        echo "Ollama started successfully (PID: $OLLAMA_PID)"
    else
        echo "WARNING: Ollama not found locally. Make sure to set OLLAMA_BASE_URL environment variable"
        echo "Example: OLLAMA_BASE_URL=http://your-ollama-server:11434"
    fi
else
    echo "Using Ollama at: $OLLAMA_BASE_URL"
fi

# Start Flask app
echo "Starting Flask application..."
exec gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 600 app:app
