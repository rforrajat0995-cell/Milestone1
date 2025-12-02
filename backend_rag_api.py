"""
Backend API for the mutual fund FAQ assistant using RAG
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os

from rag_pipeline import RAGPipeline
import config_rag

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Enable CORS for frontend integration

# Initialize RAG pipeline (lazy initialization - will be created on first use)
rag_pipeline = None

def get_rag_pipeline():
    """Lazy initialization of RAG pipeline"""
    global rag_pipeline
    if rag_pipeline is None:
        api_key = os.getenv("GOOGLE_API_KEY") or config_rag.GOOGLE_API_KEY
        if not api_key:
            logger.warning("No Google API key found. RAG pipeline may not work correctly.")
            return None
        
        try:
            rag_pipeline = RAGPipeline(api_key=api_key, use_local_embeddings=True)
            logger.info("RAG pipeline initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RAG pipeline: {e}", exc_info=True)
            rag_pipeline = None
    return rag_pipeline


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    pipeline = get_rag_pipeline()
    return jsonify({
        "status": "healthy",
        "service": "Mutual Fund FAQ Assistant (RAG)",
        "rag_ready": pipeline is not None
    })


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

