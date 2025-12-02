"""
Local embedding generation using sentence-transformers
No API key required - runs locally
"""

from typing import List, Optional
import logging

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logging.warning("sentence-transformers not installed. Run: pip install sentence-transformers")

logger = logging.getLogger(__name__)


class LocalEmbeddingGenerator:
    """Generates embeddings using local sentence-transformers model"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize local embedding generator.
        
        Args:
            model_name: Sentence transformer model name
                       Options: "all-MiniLM-L6-v2" (fast, 384 dims)
                               "all-mpnet-base-v2" (better quality, 768 dims)
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError("sentence-transformers required. Install with: pip install sentence-transformers")
        
        logger.info(f"Loading local embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        logger.info("Model loaded successfully")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        try:
            embedding = self.model.encode(text, convert_to_numpy=False)
            return embedding.tolist() if hasattr(embedding, 'tolist') else list(embedding)
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
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
                embeddings = self.model.encode(batch, convert_to_numpy=False, show_progress_bar=False)
                # Convert to list format
                if isinstance(embeddings, list):
                    all_embeddings.extend([emb.tolist() if hasattr(emb, 'tolist') else list(emb) for emb in embeddings])
                else:
                    all_embeddings.extend([emb.tolist() if hasattr(emb, 'tolist') else list(emb) for emb in embeddings])
            except Exception as e:
                logger.error(f"Error generating embeddings for batch: {e}")
                raise
        
        return all_embeddings
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for a query (same as generate_embedding for local models).
        
        Args:
            query: Query text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        return self.generate_embedding(query)

