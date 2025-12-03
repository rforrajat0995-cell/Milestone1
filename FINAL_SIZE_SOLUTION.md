# Final Solution for 250MB Limit

## Current Status
Even after removing pandas, beautifulsoup4, lxml, flask, ChromaDB alone is 100-200MB, pushing us over the 250MB limit.

## Solutions (in order of preference)

### Option 1: Replace ChromaDB with In-Memory Vector Search (RECOMMENDED)

Replace ChromaDB with a simple in-memory solution using numpy:

**New requirements.txt:**
```
google-generativeai>=0.3.0
python-dotenv>=1.0.0
numpy>=1.24.0
```

**Benefits:**
- Much smaller (~10-20MB vs 100-200MB)
- Fast enough for small datasets
- No external dependencies

**Implementation:**
- Store embeddings as JSON files
- Load into memory on first request
- Use numpy for cosine similarity search

### Option 2: Use FAISS (Lighter than ChromaDB)

**requirements.txt:**
```
google-generativeai>=0.3.0
python-dotenv>=1.0.0
faiss-cpu>=1.7.4
numpy>=1.24.0
```

**Benefits:**
- Smaller than ChromaDB (~30-50MB)
- Very fast vector search
- Industry standard

### Option 3: External Vector DB Service

Use managed services:
- **Pinecone** (free tier available)
- **Weaviate Cloud**
- **Qdrant Cloud**

**Benefits:**
- No size limits
- Better scalability
- Managed service

### Option 4: Vercel Pro + Optimizations

Upgrade to Pro tier and continue optimizing.

## Recommended: Option 1 (In-Memory)

For your use case (7 funds, small dataset), in-memory search is perfect:
- Fast enough
- Much smaller
- Simpler
- No external dependencies

## Next Steps

If you want to proceed with Option 1, I can:
1. Create a new `vector_store_simple.py` using numpy
2. Update `rag_pipeline.py` to use it
3. Store embeddings as JSON instead of ChromaDB
4. Update requirements.txt

This should bring the size down to ~50-100MB total.

