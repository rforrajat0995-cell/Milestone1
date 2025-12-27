"""
Configuration for RAG system
API keys should be set as environment variables or in a .env file
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Groq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
# Groq LLM Model - Fast inference models
GROQ_LLM_MODEL = "llama-3.1-8b-instant"  # Fast and cost-effective model ($0.05/$0.08 per million tokens)

# Note: Groq doesn't provide embeddings, so we use local embeddings (sentence-transformers)
# Keep Gemini config for backward compatibility (if needed)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_EMBEDDING_MODEL = "models/embedding-001"  # Not used with Groq
GEMINI_LLM_MODEL = "models/gemini-2.0-flash"  # Not used with Groq

# Vector Database Configuration
VECTOR_DB_TYPE = "chroma"  # Options: "chroma", "faiss", "memory"
# Use /tmp for Vercel, data/vector_db for local development
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "data/vector_db")

# RAG Configuration
CHUNK_SIZE = 500  # Characters per chunk
CHUNK_OVERLAP = 50  # Overlap between chunks
TOP_K_RETRIEVAL = 3  # Number of chunks to retrieve for context

# Answer Generation
MAX_TOKENS = 500
TEMPERATURE = 0.0  # Low temperature for factual answers

