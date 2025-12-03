"""
Vercel serverless function for health check endpoint
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import sys

# Add parent directory to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Check if RAG pipeline can be initialized
        rag_ready = False
        try:
            from rag_pipeline import RAGPipeline
            api_key = os.getenv("GOOGLE_API_KEY")
            if api_key:
                # Just check if we can import, don't actually initialize
                rag_ready = True
        except:
            pass
        
        self.wfile.write(json.dumps({
            "status": "healthy",
            "service": "Mutual Fund FAQ Assistant (RAG)",
            "rag_ready": rag_ready,
            "platform": "Vercel"
        }).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.end_headers()

