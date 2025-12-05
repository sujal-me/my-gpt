# Ollama LLM Flask API

A Flask-based API for running LLM inference using Ollama's `ministral-3:8b-cloud` model. Deploy on Render as your own personal LLM service.

## Features

- 🚀 Text generation API with configurable parameters
- 💬 Chat API with conversation history support
- 📊 Model management (list, pull models)
- 🏥 Health check endpoint
- 🔄 CORS enabled for web integration
- 📦 Docker containerized for easy deployment
- ⚡ Gunicorn production server

## Prerequisites

### Local Development
- Python 3.11+
- Ollama installed ([download here](https://ollama.ai))
- Docker (optional, for containerized testing)

### Render Deployment
- Render account ([render.com](https://render.com))
- GitHub repository with this code

## Quick Start

### Local Setup

1. **Clone the repository:**
```bash
git clone <your-repo-url>
cd my-gpt
```

2. **Install Ollama:**
- Download from [ollama.ai](https://ollama.ai)
- Install and start the Ollama service

3. **Pull the model:**
```bash
ollama pull ministral-3:8b-cloud
```

4. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

5. **Install dependencies:**
```bash
pip install -r requirements.txt
```

6. **Create `.env` file (optional):**
```env
PORT=5000
FLASK_DEBUG=False
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=ministral-3:8b-cloud
```

7. **Run the application:**
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## Docker Setup

### Build and Run Locally

```bash
docker build -t ollama-api .
docker run -p 5000:5000 \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  ollama-api
```

## Deployment on Render

### Step 1: Push to GitHub

```bash
git add .
git commit -m "Add Ollama Flask API"
git push origin main
```

### Step 2: Connect to Render

1. Go to [render.com](https://render.com)
2. Sign up/login with GitHub
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Select this repo
6. Configure:
   - **Name:** `ollama-api` (or your choice)
   - **Branch:** `main`
   - **Runtime:** `Docker`
   - **Region:** Choose closest to you
   - **Plan:** `Free` (for testing)
7. Set environment variables:
   - `PORT`: `5000`
   - `FLASK_DEBUG`: `False`
   - `DEFAULT_MODEL`: `ministral-3:8b-cloud`
   - `OLLAMA_BASE_URL`: (see options below)

### Step 3: Configure Ollama Access

**Option A: External Ollama Server** (Recommended for production)
- Set up Ollama on a separate server/instance
- Set `OLLAMA_BASE_URL` to your Ollama server URL
- Example: `http://your-ollama-server:11434`

**Option B: Local Ollama in Container** (Experimental, may timeout)
- Leave `OLLAMA_BASE_URL` unset
- Ollama will attempt to start in the container
- Note: May exceed Render's resource limits

### Step 4: Deploy

Click "Deploy" and wait for the service to build and start. You'll get a public URL like:
```
https://ollama-api.onrender.com
```

## API Endpoints

### 1. Health Check
```
GET /health
```
Check if the API and Ollama service are running.

**Response:**
```json
{
  "status": "healthy",
  "ollama": "connected",
  "base_url": "http://localhost:11434"
}
```

### 2. List Models
```
GET /api/models
```
List all available models in Ollama.

**Response:**
```json
{
  "models": [
    {
      "name": "ministral-3:8b-cloud",
      "size": 5368709120
    }
  ]
}
```

### 3. Generate Text
```
POST /api/generate
Content-Type: application/json

{
  "prompt": "What is artificial intelligence?",
  "model": "ministral-3:8b-cloud",
  "temperature": 0.7,
  "top_k": 40,
  "top_p": 0.9,
  "max_tokens": 512,
  "stream": false
}
```

**Response:**
```json
{
  "model": "ministral-3:8b-cloud",
  "prompt": "What is artificial intelligence?",
  "response": "Artificial intelligence (AI) refers to the simulation of human intelligence...",
  "done": true,
  "total_duration": 2500000000,
  "eval_count": 42,
  "eval_duration": 1500000000
}
```

**Parameters:**
- `prompt` (string, required): The input text
- `model` (string): Model name (default: `ministral-3:8b-cloud`)
- `temperature` (float): Creativity level 0-2 (default: 0.7)
- `top_k` (int): Top-K sampling (default: 40)
- `top_p` (float): Nucleus sampling (default: 0.9)
- `max_tokens` (int): Maximum output tokens (default: 512)
- `stream` (boolean): Stream response (default: false)

### 4. Chat (Conversation)
```
POST /api/chat
Content-Type: application/json

{
  "messages": [
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hi! How can I help?"},
    {"role": "user", "content": "What's the capital of France?"}
  ],
  "model": "ministral-3:8b-cloud",
  "temperature": 0.7,
  "max_tokens": 256
}
```

**Response:**
```json
{
  "model": "ministral-3:8b-cloud",
  "messages": [...],
  "response": "The capital of France is Paris.",
  "total_duration": 1500000000
}
```

### 5. Pull Model
```
POST /api/pull
Content-Type: application/json

{
  "model": "llama2"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Model llama2 pulled successfully"
}
```

## Usage Examples

### Using cURL

**Generate text:**
```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Why is the sky blue?",
    "temperature": 0.7,
    "max_tokens": 256
  }'
```

**Chat:**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is 2+2?"}
    ]
  }'
```

### Using Python

```python
import requests

API_URL = "http://localhost:5000"

# Generate text
response = requests.post(
    f"{API_URL}/api/generate",
    json={
        "prompt": "Explain quantum computing in simple terms",
        "temperature": 0.7,
        "max_tokens": 256
    }
)
print(response.json())

# Chat
response = requests.post(
    f"{API_URL}/api/chat",
    json={
        "messages": [
            {"role": "user", "content": "Hello, how are you?"},
            {"role": "assistant", "content": "I'm doing well, thanks for asking!"},
            {"role": "user", "content": "What's your name?"}
        ],
        "temperature": 0.7,
        "max_tokens": 256
    }
)
print(response.json())
```

### Using JavaScript/Node.js

```javascript
const API_URL = "http://localhost:5000";

async function generateText(prompt) {
  const response = await fetch(`${API_URL}/api/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      prompt: prompt,
      temperature: 0.7,
      max_tokens: 256
    })
  });
  return response.json();
}

// Usage
generateText("What is machine learning?").then(console.log);
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 5000 | Flask server port |
| `FLASK_DEBUG` | False | Debug mode |
| `OLLAMA_BASE_URL` | http://localhost:11434 | Ollama API base URL |
| `DEFAULT_MODEL` | ministral-3:8b-cloud | Default model to use |

## Troubleshooting

### Ollama Connection Error
```
Error: Cannot connect to Ollama service
```
- Ensure Ollama is running: `ollama serve`
- Check `OLLAMA_BASE_URL` is correct
- For Docker, use `http://host.docker.internal:11434` on macOS/Windows

### Model Not Found
```
Error: model not found
```
- Pull the model: `ollama pull ministral-3:8b-cloud`
- Check available models: `GET /api/models`

### Request Timeout
- Reduce `max_tokens` parameter
- Increase server timeout
- Use a simpler/shorter prompt

### Render Deployment Issues
- Check logs: Render dashboard → Service → Logs
- Verify environment variables are set
- Ensure Ollama server is accessible (if using external)
- For free tier, may need to upgrade for larger models

## Performance Tips

1. **Use appropriate temperature:**
   - Lower (0.1-0.3): More deterministic, better for factual queries
   - Higher (0.7-1.5): More creative, better for content generation

2. **Optimize tokens:**
   - Use smaller `max_tokens` for faster responses
   - Start with 256 tokens and increase if needed

3. **Model selection:**
   - `ministral-3:8b-cloud`: Fast, small model (good for Render)
   - Consider larger models for better quality (need better hardware)

4. **For production:**
   - Use Render's paid tier for better performance
   - Set up external Ollama server for reliability
   - Implement rate limiting/authentication

## Advanced Configuration

### Adding Authentication

Update `app.py` to add Bearer token validation:

```python
from functools import wraps

API_KEY = os.getenv("API_KEY", "default-key")

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if token != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

# Apply to endpoints:
@app.route("/api/generate", methods=["POST"])
@require_api_key
def generate():
    # ... existing code
```

### Custom Model

Change `DEFAULT_MODEL` in render.yaml or code:
```env
DEFAULT_MODEL=llama2:7b
```

Then pull it:
```bash
ollama pull llama2:7b
```

## License

MIT License - feel free to use and modify

## Support

- Ollama Documentation: https://github.com/ollama/ollama
- Flask Documentation: https://flask.palletsprojects.com
- Render Docs: https://render.com/docs

---

**Made with ❤️ for your personal LLM service**