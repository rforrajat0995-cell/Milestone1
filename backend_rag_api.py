"""
Backend API for the mutual fund FAQ assistant using RAG
"""

import logging
import os
import sys

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, use system env vars

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
            # Try with Gemini first, fallback to local if quota exceeded
            try:
                rag_pipeline = RAGPipeline(api_key=api_key, use_local_embeddings=False)
                logger.info("RAG pipeline initialized successfully with Gemini embeddings")
            except Exception as e:
                error_str = str(e).lower()
                if "quota" in error_str or "429" in error_str or "limit" in error_str:
                    logger.warning("Gemini API quota exceeded. Falling back to local embeddings...")
                    rag_pipeline = RAGPipeline(api_key=api_key, use_local_embeddings=True)
                    logger.info("RAG pipeline initialized successfully with local embeddings")
                else:
                    raise
        except Exception as e:
            logger.error(f"Failed to initialize RAG pipeline: {e}", exc_info=True)
            _rag_initialization_error = str(e)
            rag_pipeline = None
    elif _rag_initialization_error:
        return None
    return rag_pipeline


@app.route('/', methods=['GET'])
def root():
    """Root endpoint - redirects to health"""
    return jsonify({
        "service": "Mutual Fund FAQ Assistant (RAG)",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "query": "/query (POST)",
            "funds": "/funds (GET)",
            "init": "/init (POST)"
        },
        "message": "Service is running. Use /health to check status."
    }), 200


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint - must work even if RAG pipeline fails"""
    try:
        pipeline = get_rag_pipeline()
        global _rag_initialization_error
        
        # Get mode information
        mode_info = {
            "embeddings": "unknown",
            "llm": "unknown",
            "fallback_active": False
        }
        
        if pipeline:
            # Check embedding mode
            embedder_type = type(pipeline.embedder).__name__
            if "Local" in embedder_type:
                mode_info["embeddings"] = "local (sentence-transformers)"
            else:
                mode_info["embeddings"] = "gemini-api"
            
            # Check LLM mode (always Gemini for now, but fallback extraction exists)
            mode_info["llm"] = "gemini-api"
            mode_info["fallback_active"] = "Local" in embedder_type
        
        return jsonify({
            "status": "healthy",
            "service": "Mutual Fund FAQ Assistant (RAG)",
            "rag_ready": pipeline is not None,
            "rag_error": _rag_initialization_error if _rag_initialization_error else None,
            "mode": mode_info,
            "message": "Service is running. RAG pipeline may need data initialization." if not pipeline else "Service is fully operational."
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


@app.route('/debug/rag-status', methods=['GET'])
def debug_rag_status():
    """Debug endpoint to check RAG pipeline initialization status"""
    import os
    import os.path as path
    
    global rag_pipeline, _rag_initialization_error
    
    debug_info = {
        "rag_pipeline_initialized": rag_pipeline is not None,
        "initialization_error": _rag_initialization_error,
        "api_key_set": bool(os.getenv("GOOGLE_API_KEY")),
        "vector_db_path": config_rag.VECTOR_DB_PATH if config_rag else "N/A",
        "vector_db_exists": path.exists(config_rag.VECTOR_DB_PATH) if config_rag else False,
        "data_storage_exists": path.exists("data/storage/funds_database.json"),
    }
    
    # Try to get more info
    try:
        from data_storage import DataStorage
        storage = DataStorage()
        data = storage.load_data()
        debug_info["funds_in_storage"] = len(data.get("funds", {})) if data else 0
    except Exception as e:
        debug_info["storage_error"] = str(e)
    
    # Check vector store
    try:
        if path.exists(config_rag.VECTOR_DB_PATH):
            import chromadb
            client = chromadb.PersistentClient(path=config_rag.VECTOR_DB_PATH)
            collections = client.list_collections()
            debug_info["vector_db_collections"] = [c.name for c in collections]
            debug_info["vector_db_collection_count"] = len(collections)
        else:
            debug_info["vector_db_collections"] = []
            debug_info["vector_db_collection_count"] = 0
    except Exception as e:
        debug_info["vector_db_error"] = str(e)
    
    return jsonify(debug_info), 200


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
        
        logger.info(f"Received query: {query} (Request ID: {id(query)})")
        
        # Process query using RAG
        logger.info(f"Starting RAG pipeline processing for query: {query[:50]}...")
        response = pipeline.answer_query(query)
        logger.info(f"Completed RAG pipeline processing for query: {query[:50]}...")
        
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
        import os.path as path
        storage = DataStorage()
        existing_data = storage.load_data()
        
        # Check if vector DB exists
        vector_db_exists = path.exists(config_rag.VECTOR_DB_PATH) if config_rag else False
        
        if existing_data and existing_data.get("funds") and vector_db_exists:
            # Check if vector DB has data
            try:
                import chromadb
                client = chromadb.PersistentClient(path=config_rag.VECTOR_DB_PATH)
                collections = client.list_collections()
                if collections:
                    logger.info("Data and vector DB already exist, skipping initialization")
                    return jsonify({
                        "success": True,
                        "message": "Data already initialized",
                        "funds_count": len(existing_data.get("funds", {})),
                        "vector_db_collections": len(collections)
                    }), 200
            except Exception as e:
                logger.warning(f"Vector DB check failed: {e}, will rebuild index")
        
        # If data exists but vector DB doesn't, just rebuild index
        if existing_data and existing_data.get("funds"):
            logger.info("Data exists but vector DB missing, rebuilding index only...")
            # Skip scraper, just build index
            result2 = subprocess.run(
                [sys.executable, 'build_rag_index.py'], 
                capture_output=True, 
                text=True, 
                timeout=600,
                cwd=os.getcwd()
            )
            
            if result2.returncode != 0:
                logger.error(f"Index builder failed: {result2.stderr}")
                return jsonify({
                    "success": False,
                    "error": "Index builder failed",
                    "details": result2.stderr[-500:] if result2.stderr else "Unknown error"
                }), 500
            
            logger.info("Index rebuilt successfully")
            return jsonify({
                "success": True,
                "message": "Vector index rebuilt successfully",
                "funds_count": len(existing_data.get("funds", {})),
                "index_output": result2.stdout[-200:] if result2.stdout else "No output"
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


# For local development only
if __name__ == '__main__':
    # Use port 5001 by default (5000 is often used by AirPlay on macOS)
    port = int(os.getenv('PORT', 5001))
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

