"""
Backend API for the mutual fund FAQ assistant
Simple REST-like interface for answering queries
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

from query_handler import QueryHandler
from data_storage import DataStorage

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Initialize components
storage = DataStorage()
query_handler = QueryHandler(storage)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Groww MF FAQ Assistant Backend"
    })


@app.route('/query', methods=['POST'])
def handle_query():
    """
    Handle query requests.
    
    Request body:
    {
        "query": "Tell me the exit load for Parag Parikh Liquid Fund Direct Growth?"
    }
    
    Response:
    {
        "success": true,
        "answer": "The Exit Load for Parag Parikh Liquid Fund Direct Growth is Nil.",
        "fund_name": "Parag Parikh Liquid Fund Direct Growth",
        "field": "exit_load",
        "value": "Nil",
        "source_url": "https://groww.in/mutual-funds/...",
        "query": "..."
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'query' in request body"
            }), 400
        
        query = data['query']
        logger.info(f"Received query: {query}")
        
        # Process query
        response = query_handler.answer_query(query)
        
        return jsonify(response), 200 if response.get("success") else 404
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/funds', methods=['GET'])
def list_funds():
    """List all available funds"""
    try:
        funds = storage.get_all_funds()
        return jsonify({
            "success": True,
            "count": len(funds),
            "funds": [{"fund_name": f["fund_name"]} for f in funds]
        }), 200
    except Exception as e:
        logger.error(f"Error listing funds: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/fund/<fund_name>', methods=['GET'])
def get_fund_info(fund_name: str):
    """Get all information about a specific fund"""
    try:
        fund_data = query_handler.get_fund_info(fund_name)
        
        if not fund_data:
            return jsonify({
                "success": False,
                "error": f"Fund '{fund_name}' not found"
            }), 404
        
        return jsonify({
            "success": True,
            "fund": fund_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting fund info: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == '__main__':
    print("="*70)
    print("Groww MF FAQ Assistant - Backend API")
    print("="*70)
    print("\nStarting server on http://localhost:5000")
    print("\nEndpoints:")
    print("  POST /query - Answer queries about mutual funds")
    print("  GET  /funds - List all available funds")
    print("  GET  /fund/<name> - Get fund information")
    print("  GET  /health - Health check")
    print("\n" + "="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

