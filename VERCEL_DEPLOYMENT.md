# Deploy Everything on Vercel Only

This guide explains how to deploy both frontend and backend on Vercel using serverless functions.

## ⚠️ Important Considerations

### Challenges with Vercel-Only Deployment:

1. **ChromaDB Persistence**: ChromaDB stores data in files (`data/vector_db/`). Vercel serverless functions are stateless and don't have persistent file storage.

2. **Cold Starts**: Each serverless function call may need to initialize the RAG pipeline, which can take 5-10 seconds on first request.

3. **Memory Limits**: Vercel serverless functions have memory limits (1GB on Pro plan, 1024MB on Hobby).

4. **Timeout Limits**: 
   - Hobby: 10 seconds
   - Pro: 60 seconds
   - Enterprise: 300 seconds

### Solutions:

**Option A: Use `/tmp` directory (Temporary, but works)**
- ChromaDB can use `/tmp` for storage
- Data persists during function execution
- **Limitation**: Data is lost when function container is recycled (usually after inactivity)

**Option B: Rebuild index on each request (Not recommended)**
- Very slow (30-60 seconds per request)
- High API costs
- Poor user experience

**Option C: Use external storage (Recommended for production)**
- Store ChromaDB data in S3, Google Cloud Storage, or similar
- Or use a managed vector database (Pinecone, Weaviate, etc.)

**Option D: Hybrid approach (Best balance)**
- Use Vercel for frontend
- Use Render/Railway for backend (as originally planned)

---

## 🚀 Option A: Vercel-Only with `/tmp` Storage

This approach uses Vercel's `/tmp` directory for ChromaDB. Data persists during function execution but may be lost on container recycle.

### Step 1: Create Vercel Serverless Functions

Create `api/query.py`:

```python
from http.server import BaseHTTPRequestHandler
import json
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag_pipeline import RAGPipeline
import config_rag

# Initialize RAG pipeline (cached across requests in same container)
rag_pipeline = None

def get_rag_pipeline():
    global rag_pipeline
    if rag_pipeline is None:
        # Use /tmp for ChromaDB storage
        os.environ['VECTOR_DB_PATH'] = '/tmp/vector_db'
        
        api_key = os.getenv("GOOGLE_API_KEY")
        rag_pipeline = RAGPipeline(api_key=api_key, use_local_embeddings=True)
    return rag_pipeline

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != '/api/query':
            self.send_response(404)
            self.end_headers()
            return
        
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            query = data.get('query', '').strip()
            if not query:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": False,
                    "error": "Query cannot be empty"
                }).encode())
                return
            
            # Get RAG pipeline
            pipeline = get_rag_pipeline()
            
            # Process query
            response = pipeline.answer_query(query)
            
            # Format response
            formatted_response = {
                "success": response.get("success", False),
                "answer": response.get("answer", ""),
                "source_urls": response.get("source_urls", []),
                "query": query,
                "retrieved_chunks": response.get("retrieved_chunks", 0)
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(formatted_response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": False,
                "error": str(e)
            }).encode())
    
    def do_GET(self):
        if self.path == '/api/health':
            pipeline = get_rag_pipeline()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "healthy",
                "service": "Mutual Fund FAQ Assistant (RAG)",
                "rag_ready": pipeline is not None
            }).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
```

Create `api/funds.py`:

```python
from http.server import BaseHTTPRequestHandler
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_storage import DataStorage

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
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
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": True,
                "count": len(fund_list),
                "funds": fund_list
            }).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": False,
                "error": str(e)
            }).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
```

### Step 2: Update Config for Vercel

Update `config_rag.py` to use `/tmp` for ChromaDB:

```python
# Vector Database Configuration
VECTOR_DB_TYPE = "chroma"
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "/tmp/vector_db")  # Use /tmp for Vercel
```

### Step 3: Initialize Data on First Request

Since we can't run initialization scripts on Vercel, we need to initialize data on first request or use a build script.

Create `api/init.py` (optional, for manual initialization):

```python
from http.server import BaseHTTPRequestHandler
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main  # Run scraper
import build_rag_index  # Build index

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Initialize data
            # This will take 30-60 seconds
            # Only run once or when data needs updating
            
            # Run scraper
            # main.main()  # Uncomment if needed
            
            # Build index
            # build_rag_index.main()  # Uncomment if needed
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": True,
                "message": "Data initialized"
            }).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": False,
                "error": str(e)
            }).encode())
```

### Step 4: Update Frontend API URL

Update `frontend/src/App.jsx`:

```jsx
// Use relative path for Vercel
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'
```

### Step 5: Deploy to Vercel

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Login**:
   ```bash
   vercel login
   ```

3. **Deploy**:
   ```bash
   vercel
   ```

4. **Add Environment Variables**:
   - Go to Vercel Dashboard → Your Project → Settings → Environment Variables
   - Add: `GOOGLE_API_KEY=your_key`

5. **Build Frontend**:
   - Vercel will auto-detect and build the frontend
   - Ensure `frontend/package.json` has build script

### Step 6: Initialize Data

**Option 1: Pre-build script** (Recommended)
- Create a build script that initializes data before deployment
- Store data in a way that's accessible to serverless functions

**Option 2: First request initialization** (Not recommended)
- Initialize on first API call
- Very slow first request (30-60 seconds)
- May timeout on free tier

**Option 3: Manual initialization endpoint**
- Create `/api/init` endpoint
- Call it once after deployment
- Takes 30-60 seconds

---

## ⚠️ Limitations

1. **Data Persistence**: ChromaDB data in `/tmp` is lost when container is recycled
2. **Cold Starts**: First request after inactivity takes 5-10 seconds
3. **Timeout**: Free tier has 10-second timeout (may not be enough for RAG)
4. **Memory**: Large models may exceed memory limits

---

## ✅ Recommended: Hybrid Approach

**Best Practice**: 
- **Frontend**: Vercel (excellent for React/Vite)
- **Backend**: Render/Railway (better for Flask + persistent storage)

This gives you:
- ✅ Fast frontend (Vercel CDN)
- ✅ Persistent backend storage
- ✅ No cold starts
- ✅ Better performance
- ✅ Lower costs

---

## 📊 Comparison

| Feature | Vercel-Only | Hybrid (Vercel + Render) |
|---------|------------|---------------------------|
| Setup Complexity | High | Medium |
| Data Persistence | Limited | Full |
| Cold Starts | Yes (5-10s) | No |
| Timeout Limits | 10s (free) | 60s+ |
| Memory Limits | 1GB | Unlimited |
| Cost | Free (limited) | Free (Render) + Free (Vercel) |
| Performance | Slow first request | Fast always |

---

## 🎯 Recommendation

**For Production**: Use **Hybrid Approach** (Vercel frontend + Render backend)

**For Testing/Prototyping**: Vercel-only is fine if you accept the limitations.

Would you like me to:
1. Create the Vercel serverless function files?
2. Set up the hybrid approach instead?
3. Help with external storage solution (S3, etc.)?

