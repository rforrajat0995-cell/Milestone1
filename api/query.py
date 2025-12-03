"""
Vercel serverless function for query endpoint
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import shutil
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Global pipeline cache (persists within same container)
rag_pipeline = None
_data_initialized = False

def initialize_data():
    """Copy data files to /tmp and initialize RAG pipeline"""
    global rag_pipeline, _data_initialized
    
    if _data_initialized and rag_pipeline:
        return rag_pipeline
    
    try:
        logger.info("Initializing RAG pipeline for Vercel...")
        
        # Set vector DB path to /tmp
        os.environ['VECTOR_DB_PATH'] = '/tmp/vector_db'
        
        # Copy vector DB from project to /tmp if it doesn't exist
        source_db = os.path.join(project_root, 'data/vector_db')
        target_db = '/tmp/vector_db'
        
        if os.path.exists(source_db) and not os.path.exists(target_db):
            logger.info("Copying vector DB to /tmp...")
            shutil.copytree(source_db, target_db)
            logger.info("Vector DB copied successfully")
        elif os.path.exists(target_db):
            logger.info("Vector DB already exists in /tmp")
        else:
            logger.warning(f"Source vector DB not found at: {source_db}")
        
        # Initialize RAG pipeline
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.error("GOOGLE_API_KEY not set")
            return None
        
        from rag_pipeline import RAGPipeline
        rag_pipeline = RAGPipeline(api_key=api_key, use_local_embeddings=True)
        _data_initialized = True
        logger.info("RAG pipeline initialized successfully")
        return rag_pipeline
        
    except Exception as e:
        logger.error(f"Failed to initialize RAG pipeline: {e}", exc_info=True)
        return None

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
            else:
                data = {}
            
            query = data.get('query', '').strip()
            if not query:
                self.wfile.write(json.dumps({
                    "success": False,
                    "error": "Query cannot be empty"
                }).encode())
                return
            
            logger.info(f"Received query: {query}")
            
            # Initialize pipeline (lazy initialization)
            pipeline = initialize_data()
            if not pipeline:
                self.wfile.write(json.dumps({
                    "success": False,
                    "error": "RAG pipeline not initialized. Please check logs."
                }).encode())
                return
            
            # Process query
            response = pipeline.answer_query(query)
            
            self.wfile.write(json.dumps({
                "success": response.get("success", False),
                "answer": response.get("answer", ""),
                "source_urls": response.get("source_urls", []),
                "query": query,
                "retrieved_chunks": response.get("retrieved_chunks", 0)
            }).encode())
            
        except Exception as e:
            logger.error(f"Error processing query: {e}", exc_info=True)
            self.wfile.write(json.dumps({
                "success": False,
                "error": str(e)
            }).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

