"""
Embedding generation module for RAG system
Uses Google Gemini embeddings API
"""

import os
from typing import List, Optional
import logging

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("Google Generative AI library not installed. Run: pip install google-generativeai")

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generates embeddings using Google Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "models/embedding-001"):
        if not GEMINI_AVAILABLE:
            raise ImportError("Google Generative AI library required. Install with: pip install google-generativeai")
        
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key not provided. Set GOOGLE_API_KEY environment variable or pass api_key parameter.")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = model
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        try:
            result = genai.embed_content(
                model=self.model,
                content=text,
                task_type="RETRIEVAL_DOCUMENT"  # Use RETRIEVAL_QUERY for queries
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches.
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process in each batch
            
        Returns:
            List of embedding vectors
        """
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            logger.info(f"Generating embeddings for batch {i//batch_size + 1} ({len(batch)} texts)")
            
            try:
                # Gemini can handle batch embedding
                result = genai.embed_content(
                    model=self.model,
                    content=batch,
                    task_type="RETRIEVAL_DOCUMENT"
                )
                batch_embeddings = result['embedding'] if isinstance(result['embedding'][0], list) else [result['embedding']]
                all_embeddings.extend(batch_embeddings)
            except Exception as e:
                logger.error(f"Error generating embeddings for batch: {e}")
                # Fallback to individual embeddings
                logger.info("Falling back to individual embeddings...")
                for text in batch:
                    embedding = self.generate_embedding(text)
                    all_embeddings.append(embedding)
        
        return all_embeddings
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for a query (uses RETRIEVAL_QUERY task type).
        
        Args:
            query: Query text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        import time
        start_time = time.time()
        logger.info(f"[EMBEDDING API] Calling genai.embed_content for query: '{query[:50]}...'")
        try:
            result = genai.embed_content(
                model=self.model,
                content=query,
                task_type="RETRIEVAL_QUERY"
            )
            elapsed = time.time() - start_time
            logger.info(f"[EMBEDDING API] ✓ Success (took {elapsed:.2f}s)")
            return result['embedding']
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"[EMBEDDING API] ✗ Error after {elapsed:.2f}s: {e}")
            raise

