# RAG System Implementation

## Overview

This is a proper **Retrieval Augmented Generation (RAG)** system that uses:
- **OpenAI Embeddings** for semantic search
- **ChromaDB** for vector storage
- **OpenAI GPT** for answer generation
- **Source URL tracking** for every answer

## Architecture

```
Query → Embed Query → Vector Search → Retrieve Chunks → 
LLM Generation (with context) → Answer + Source URL
```

## Setup

### 1. Install Dependencies

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Set API Key

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

Or set as environment variable:

```bash
export OPENAI_API_KEY=sk-your-actual-api-key-here
```

Get your API key from: https://platform.openai.com/api-keys

### 3. Collect Data (if not done already)

```bash
python data_storage.py
```

This scrapes and stores all fund data.

### 4. Build Vector Index

```bash
python build_rag_index.py
```

This will:
- Load stored fund data
- Create text chunks
- Generate embeddings using OpenAI
- Store in ChromaDB vector database

### 5. Test RAG System

```bash
python test_rag.py
```

## Usage

### Programmatic Usage

```python
from rag_pipeline import RAGPipeline
import os

# Initialize with API key
api_key = os.getenv("OPENAI_API_KEY")
pipeline = RAGPipeline(api_key=api_key)

# Answer a query
query = "Tell me the exit load for Parag Parikh Liquid Fund Direct Growth?"
response = pipeline.answer_query(query)

print(response['answer'])
print(f"Source: {response['source_urls'][0]}")
```

### Integration with Backend API

Update `backend_api.py` to use RAG instead of keyword matching:

```python
from rag_pipeline import RAGPipeline

# Initialize RAG pipeline
rag_pipeline = RAGPipeline(api_key=os.getenv("OPENAI_API_KEY"))

@app.route('/query', methods=['POST'])
def handle_query():
    query = request.json['query']
    response = rag_pipeline.answer_query(query)
    return jsonify(response)
```

## Components

### 1. Data Chunking (`data_chunking.py`)
- Converts structured fund data into text chunks
- Creates both comprehensive and field-specific chunks
- Includes source URLs in metadata

### 2. Embeddings (`embeddings.py`)
- Uses OpenAI `text-embedding-3-small` model
- Generates embeddings for chunks and queries
- Batch processing for efficiency

### 3. Vector Store (`vector_store.py`)
- Uses ChromaDB for persistent storage
- Stores embeddings with metadata
- Semantic search functionality

### 4. RAG Pipeline (`rag_pipeline.py`)
- Main orchestration component
- Handles retrieval and generation
- Ensures source URLs in answers

## Configuration

Edit `config_rag.py` to customize:

- **Embedding Model**: `text-embedding-3-small` (cost-effective)
- **LLM Model**: `gpt-4o-mini` (fast) or `gpt-4` (better quality)
- **Top K Retrieval**: Number of chunks to retrieve (default: 3)
- **Chunk Size**: Text chunk size (default: 500 chars)

## Cost Estimation

Using `gpt-4o-mini` and `text-embedding-3-small`:

- **Embedding**: ~$0.02 per 1M tokens
- **Generation**: ~$0.15 per 1M input tokens, $0.60 per 1M output tokens

For ~50 chunks and typical queries:
- Index building: ~$0.001 (one-time)
- Per query: ~$0.0001-0.001

## Features

✅ **True RAG**: Semantic search + LLM generation  
✅ **Source URLs**: Every answer includes source  
✅ **Facts Only**: No investment advice  
✅ **Persistent Storage**: ChromaDB saves embeddings  
✅ **Efficient**: Batch processing and caching  

## Troubleshooting

**Error: API key not found**
- Check `.env` file exists and has `OPENAI_API_KEY`
- Or set environment variable

**Error: Vector index empty**
- Run `python build_rag_index.py` first

**Error: No fund data**
- Run `python data_storage.py` to collect data first

## Next Steps

1. **Add more data sources**: FAQ pages, help articles
2. **Improve chunking**: Better text segmentation
3. **Add reranking**: Improve retrieval quality
4. **Caching**: Cache common queries
5. **Monitoring**: Track costs and performance

