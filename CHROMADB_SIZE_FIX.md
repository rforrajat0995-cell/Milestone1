# ChromaDB Size Fix for Vercel

## Problem
ChromaDB alone is 100-200MB+, causing the 250MB limit to be exceeded.

## Solutions

### Option 1: Use excludeFiles (Applied)
Added `excludeFiles` to `vercel.json` to exclude unnecessary files:
- Python cache files
- Test files
- Documentation
- Examples

### Option 2: Minimal ChromaDB Installation
Trying to install ChromaDB with minimal dependencies using `--no-deps` and only including core dependencies.

### Option 3: Alternative Approaches (If still too large)

#### A. Use FAISS (Lighter alternative)
Replace ChromaDB with FAISS:
```python
# requirements.txt
faiss-cpu>=1.7.4
numpy>=1.24.0
```

#### B. Use External Vector DB
- Pinecone (managed service)
- Weaviate Cloud
- Qdrant Cloud

#### C. Build Vector DB On-Demand
Instead of including pre-built vector DB:
1. Store embeddings in JSON files
2. Load into memory on first request
3. Use simple cosine similarity search

#### D. Use Vercel Pro
Upgrade to Pro tier for higher limits (but still may hit limits).

## Current Status
Applied Option 1 and 2. If still failing, we'll need to implement Option 3.

