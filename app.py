import os
import subprocess
import time
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import ollama
import subprocess
subprocess.run(["bash", "-c", "curl -fsSL https://ollama.com/install.sh | sh"])
process = subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

time.sleep(5)
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Ollama configuration
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "ministral-3:8b-cloud")

def is_ollama_installed():
    """Check if Ollama is installed on the system."""
    try:
        result = subprocess.run(["which", "ollama"], capture_output=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def check_ollama_running():
    """Check if Ollama service is running."""
    try:
        ollama.list()
        return True
    except:
        return False

def start_ollama_background():
    """Start Ollama in a background process."""
    try:
        logger.info("Starting Ollama service in background...")
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(5)  # Wait for Ollama to start
        logger.info("Ollama service started!")
        return True
    except Exception as e:
        logger.error(f"Failed to start Ollama: {str(e)}")
        return False

def pull_model(model_name):
    """Pull a model from Ollama."""
    try:
        logger.info(f"Pulling model: {model_name}...")
        ollama.pull(model_name)
        logger.info(f"Model {model_name} pulled successfully!")
        return True
    except Exception as e:
        logger.error(f"Failed to pull model: {str(e)}")
        return False

def ensure_ollama_ready():
    """Ensure Ollama is ready before starting the app."""
    logger.info("Checking Ollama availability...")
    
    # Check if Ollama is already running
    if check_ollama_running():
        logger.info("Ollama is already running!")
        return True
    
    # Check if Ollama is installed
    if not is_ollama_installed():
        logger.warning("Ollama is not installed!")
        logger.warning("Install from: https://ollama.ai")
        return False
    
    # Start Ollama if installed but not running
    logger.info("Ollama is installed but not running. Starting it now...")
    if not start_ollama_background():
        return False
    
    # Verify Ollama is running
    if not check_ollama_running():
        logger.error("Failed to start Ollama service")
        return False
    
    logger.info("Ollama started successfully!")
    return True

# Health check endpoint
@app.route("/health", methods=["GET"])
def health():
    """Check if the API and Ollama service are running."""
    try:
        ollama.list()
        return jsonify({
            "status": "healthy",
            "ollama": "connected"
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "message": str(e)
        }), 503

@app.route("/api/models", methods=["GET"])
def list_models():
    """List all available models in Ollama."""
    try:
        models = ollama.list()
        model_list = [{"name": model.model} for model in models.models] if models.models else []
        return jsonify({
            "models": model_list
        }), 200
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/generate", methods=["POST"])
def generate():
    """Generate text using Ollama model."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        prompt = data.get("prompt")
        model = data.get("model", DEFAULT_MODEL)
        temperature = data.get("temperature", 0.7)
        top_k = data.get("top_k", 40)
        top_p = data.get("top_p", 0.9)
        num_predict = data.get("num_predict", 512)
        
        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400
        
        logger.info(f"Generating with model: {model}")
        
        # Generate using Ollama Python library
        response = ollama.generate(
            model=model,
            prompt=prompt,
            stream=False,
            options={
                "temperature": temperature,
                "top_k": top_k,
                "top_p": top_p,
                "num_predict": num_predict,
            }
        )
        
        return jsonify({
            "model": model,
            "prompt": prompt,
            "response": response["response"],
            "done": response.get("done", True),
            "total_duration": response.get("total_duration", 0),
            "load_duration": response.get("load_duration", 0),
            "prompt_eval_count": response.get("prompt_eval_count", 0),
            "prompt_eval_duration": response.get("prompt_eval_duration", 0),
            "eval_count": response.get("eval_count", 0),
            "eval_duration": response.get("eval_duration", 0)
        }), 200
        
    except Exception as e:
        logger.error(f"Error during generation: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/chat", methods=["POST"])
def chat():
    """Chat endpoint with conversation history support."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        messages = data.get("messages", [])
        model = data.get("model", DEFAULT_MODEL)
        temperature = data.get("temperature", 0.7)
        num_predict = data.get("num_predict", 512)
        
        if not messages:
            return jsonify({"error": "Messages are required"}), 400
        
        logger.info(f"Chat with model: {model}")
        
        # Use Ollama's chat function
        response = ollama.chat(
            model=model,
            messages=messages,
            stream=False,
            options={
                "temperature": temperature,
                "num_predict": num_predict,
            }
        )
        
        assistant_response = response.get("message", {}).get("content", "")
        
        return jsonify({
            "model": model,
            "messages": messages,
            "response": assistant_response,
            "total_duration": response.get("total_duration", 0)
        }), 200
        
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/pull", methods=["POST"])
def pull():
    """Pull a model from Ollama."""
    try:
        data = request.get_json()
        model_name = data.get("model") if data else None
        
        if not model_name:
            return jsonify({"error": "Model name is required"}), 400
        
        logger.info(f"Pulling model: {model_name}")
        
        if pull_model(model_name):
            return jsonify({
                "status": "success",
                "message": f"Model {model_name} pulled successfully"
            }), 200
        else:
            return jsonify({
                "error": "Failed to pull model"
            }), 500
            
    except Exception as e:
        logger.error(f"Error pulling model: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["GET"])
def index():
    """API information and usage guide."""
    return jsonify({
        "name": "Ollama LLM API",
        "version": "1.0.0",
        "model": DEFAULT_MODEL,
        "endpoints": {
            "GET /": "This help message",
            "GET /health": "Health check",
            "GET /api/models": "List available models",
            "POST /api/generate": "Generate text from prompt",
            "POST /api/chat": "Chat with conversation history",
            "POST /api/pull": "Pull a model from Ollama"
        },
        "example_generate": {
            "endpoint": "/api/generate",
            "method": "POST",
            "body": {
                "prompt": "What is machine learning?",
                "model": "ministral-3:8b-cloud",
                "temperature": 0.7,
                "num_predict": 512
            }
        },
        "example_chat": {
            "endpoint": "/api/chat",
            "method": "POST",
            "body": {
                "messages": [
                    {"role": "user", "content": "Hello!"},
                    {"role": "assistant", "content": "Hi there! How can I help?"},
                    {"role": "user", "content": "What's 2+2?"}
                ],
                "model": "ministral-3:8b-cloud",
                "temperature": 0.7,
                "num_predict": 512
            }
        }
    }), 200

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "False") == "True"
    
    logger.info("=" * 60)
    logger.info("Ollama LLM API - Starting Up")
    logger.info("=" * 60)
    logger.info(f"Default model: {DEFAULT_MODEL}")
    
    # Ensure Ollama is ready
    if not ensure_ollama_ready():
        logger.warning("WARNING: Could not start Ollama. API will be available but may not work until Ollama is running.")
    else:
        # Pull the default model
        pull_model(DEFAULT_MODEL)
    
    logger.info("=" * 60)
    logger.info(f"Starting Flask app on port {port}")
    logger.info("=" * 60)
    app.run(host="0.0.0.0", port=port, debug=debug)
