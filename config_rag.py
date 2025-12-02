"""
Configuration for RAG system
API keys should be set as environment variables or in a .env file
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Google Gemini API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_EMBEDDING_MODEL = "models/embedding-001"  # Gemini embedding model
GEMINI_LLM_MODEL = "models/gemini-2.0-flash"  # Fast and cost-effective. Options: "models/gemini-2.0-flash", "models/gemini-2.5-flash", "models/gemini-2.5-pro"

# Vector Database Configuration
VECTOR_DB_TYPE = "chroma"  # Options: "chroma", "faiss", "memory"
VECTOR_DB_PATH = "data/vector_db"

# RAG Configuration
CHUNK_SIZE = 500  # Characters per chunk
CHUNK_OVERLAP = 50  # Overlap between chunks
TOP_K_RETRIEVAL = 3  # Number of chunks to retrieve for context

# Answer Generation
MAX_TOKENS = 500
TEMPERATURE = 0.0  # Low temperature for factual answers

