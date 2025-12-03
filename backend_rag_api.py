"""
Backend API for the mutual fund FAQ assistant using RAG
"""

import logging
import os
import sys

# Setup logging first - before any imports that might fail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

logger.info("="*70)
logger.info("Initializing backend_rag_api module...")
logger.info("="*70)

try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    logger.info("✓ Flask and CORS imported successfully")
except Exception as e:
    logger.error(f"✗ Failed to import Flask: {e}", exc_info=True)
    raise

try:
    from rag_pipeline import RAGPipeline
    import config_rag
    logger.info("✓ RAG pipeline modules imported successfully")
except Exception as e:
    logger.warning(f"⚠ Failed to import RAG modules: {e}")
    logger.warning("⚠ App will start but RAG features won't work")
    RAGPipeline = None
    config_rag = None

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Enable CORS for frontend integration

# Initialize RAG pipeline (lazy initialization - will be created on first use)
rag_pipeline = None
_rag_initialization_error = None

def get_rag_pipeline():
    """Lazy initialization of RAG pipeline"""
    global rag_pipeline, _rag_initialization_error
    
    if RAGPipeline is None:
        logger.warning("RAGPipeline not available (import failed)")
        return None
    
    if rag_pipeline is None and _rag_initialization_error is None:
        api_key = os.getenv("GOOGLE_API_KEY")
        if config_rag:
            api_key = api_key or getattr(config_rag, 'GOOGLE_API_KEY', None)
        
        if not api_key:
            logger.warning("No Google API key found. RAG pipeline may not work correctly.")
            _rag_initialization_error = "No API key"
            return None
        
        try:
            logger.info("Attempting to initialize RAG pipeline...")
            rag_pipeline = RAGPipeline(api_key=api_key, use_local_embeddings=True)
            logger.info("RAG pipeline initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RAG pipeline: {e}", exc_info=True)
            _rag_initialization_error = str(e)
            rag_pipeline = None
    elif _rag_initialization_error:
        return None
    return rag_pipeline


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint - must work even if RAG pipeline fails"""
    try:
        pipeline = get_rag_pipeline()
        return jsonify({
            "status": "healthy",
            "service": "Mutual Fund FAQ Assistant (RAG)",
            "rag_ready": pipeline is not None,
            "message": "Service is running. RAG pipeline may need data initialization."
        })
    except Exception as e:
        # Health check should always succeed
        logger.error(f"Error in health check: {e}")
        return jsonify({
            "status": "healthy",
            "service": "Mutual Fund FAQ Assistant (RAG)",
            "rag_ready": False,
            "error": "RAG pipeline not ready"
        }), 200


@app.route('/query', methods=['POST'])
def handle_query():
    """
    Handle query requests using RAG.
    
    Request body:
    {
        "query": "What is the exit load for Parag Parikh ELSS Tax Saver Fund?"
    }
    
    Response:
    {
        "success": true,
        "answer": "The exit load for Parag Parikh ELSS Tax Saver Fund Direct Growth is Nil.",
        "source_urls": ["https://groww.in/mutual-funds/..."],
        "query": "...",
        "retrieved_chunks": 5
    }
    """
    pipeline = get_rag_pipeline()
    if not pipeline:
        return jsonify({
            "success": False,
            "error": "RAG pipeline not initialized. Please check logs and ensure data is initialized."
        }), 500
    
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'query' in request body"
            }), 400
        
        query = data['query'].strip()
        
        if not query:
            return jsonify({
                "success": False,
                "error": "Query cannot be empty"
            }), 400
        
        logger.info(f"Received query: {query}")
        
        # Process query using RAG
        response = pipeline.answer_query(query)
        
        # Format response for frontend
        formatted_response = {
            "success": response.get("success", False),
            "answer": response.get("answer", ""),
            "source_urls": response.get("source_urls", []),
            "query": query,
            "retrieved_chunks": response.get("retrieved_chunks", 0)
        }
        
        return jsonify(formatted_response), 200
        
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/funds', methods=['GET'])
def list_funds():
    """List all available funds"""
    try:
        from data_storage import DataStorage
        storage = DataStorage()
        funds_data = storage.load_data()
        funds = funds_data.get("funds", {})
        
        fund_list = [
            {
                "fund_name": fund_data.get("fund_name"),
                "source_url": fund_data.get("source_url")
            }
            for fund_data in funds.values()
        ]
        
        return jsonify({
            "success": True,
            "count": len(fund_list),
            "funds": fund_list
        }), 200
    except Exception as e:
        logger.error(f"Error listing funds: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/init', methods=['POST'])
def initialize_data():
    """
    Initialize data - call this once after deployment.
    This allows data initialization without shell access.
    """
    import subprocess
    import sys
    import os
    
    logger.info("Data initialization requested")
    
    try:
        # Check if data already exists
        from data_storage import DataStorage
        storage = DataStorage()
        existing_data = storage.load_data()
        
        if existing_data and existing_data.get("funds"):
            logger.info("Data already exists, skipping initialization")
            return jsonify({
                "success": True,
                "message": "Data already initialized",
                "funds_count": len(existing_data.get("funds", {}))
            }), 200
        
        # Run scraper
        logger.info("Running scraper...")
        result1 = subprocess.run(
            [sys.executable, 'main.py'], 
            capture_output=True, 
            text=True, 
            timeout=600,  # 10 minute timeout
            cwd=os.getcwd()
        )
        
        if result1.returncode != 0:
            logger.error(f"Scraper failed: {result1.stderr}")
            return jsonify({
                "success": False,
                "error": "Scraper failed",
                "details": result1.stderr[-500:] if result1.stderr else "Unknown error"
            }), 500
        
        # Run index builder
        logger.info("Building RAG index...")
        result2 = subprocess.run(
            [sys.executable, 'build_rag_index.py'], 
            capture_output=True, 
            text=True, 
            timeout=600,  # 10 minute timeout
            cwd=os.getcwd()
        )
        
        if result2.returncode != 0:
            logger.error(f"Index builder failed: {result2.stderr}")
            return jsonify({
                "success": False,
                "error": "Index builder failed",
                "details": result2.stderr[-500:] if result2.stderr else "Unknown error"
            }), 500
        
        logger.info("Data initialization completed successfully")
        return jsonify({
            "success": True,
            "message": "Data initialized successfully",
            "scraper_output": result1.stdout[-200:] if result1.stdout else "No output",
            "index_output": result2.stdout[-200:] if result2.stdout else "No output"
        }), 200
        
    except subprocess.TimeoutExpired:
        logger.error("Initialization timed out")
        return jsonify({
            "success": False,
            "error": "Initialization timed out (takes 5-10 minutes)"
        }), 500
    except Exception as e:
        logger.error(f"Initialization error: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# This ensures the app can be imported by gunicorn
if __name__ == '__main__':
    # Get port from environment variable (for Railway/Heroku) or default to 5000
    port = int(os.getenv('PORT', 5000))
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print("="*70)
    print("Mutual Fund FAQ Assistant - RAG Backend API")
    print("="*70)
    print(f"\nStarting server on port {port}")
    print("\nEndpoints:")
    print("  POST /query - Answer queries about mutual funds (RAG)")
    print("  GET  /funds - List all available funds")
    print("  GET  /health - Health check")
    print("\n" + "="*70 + "\n")
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)

