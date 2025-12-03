"""
Vercel serverless function for listing funds
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
        
        try:
            from data_storage import DataStorage
            storage = DataStorage()
            funds_data = storage.load_data()
            funds = funds_data.get("funds", {}) if funds_data else {}
            
            fund_list = [
                {
                    "fund_name": fund_data.get("fund_name"),
                    "source_url": fund_data.get("source_url")
                }
                for fund_data in funds.values()
            ]
            
            self.wfile.write(json.dumps({
                "success": True,
                "count": len(fund_list),
                "funds": fund_list
            }).encode())
        except Exception as e:
            self.wfile.write(json.dumps({
                "success": False,
                "error": str(e)
            }).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.end_headers()

