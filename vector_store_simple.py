"""
Simple in-memory vector store using numpy
Lightweight alternative to ChromaDB for Vercel deployment
"""

import os
import json
import numpy as np
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class SimpleVectorStore:
    """Lightweight in-memory vector database using numpy"""
    
    def __init__(self, db_path: str = "data/vector_db", collection_name: str = "mutual_funds"):
        self.db_path = db_path
        self.collection_name = collection_name
        
        # In-memory storage
        self.embeddings: List[np.ndarray] = []
        self.chunks: List[Dict] = []
        self.metadatas: List[Dict] = []
        
        # Load from JSON if exists
        self._load_from_json()
    
    def _get_json_path(self) -> str:
        """Get path to JSON file for persistence"""
        os.makedirs(self.db_path, exist_ok=True)
        return os.path.join(self.db_path, f"{self.collection_name}.json")
    
    def _load_from_json(self):
        """Load embeddings and chunks from JSON file"""
        json_path = self._get_json_path()
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r') as f:
                    data = json.load(f)
                    self.embeddings = [np.array(emb) for emb in data.get('embeddings', [])]
                    self.chunks = data.get('chunks', [])
                    self.metadatas = data.get('metadatas', [])
                logger.info(f"Loaded {len(self.chunks)} chunks from {json_path}")
            except Exception as e:
                logger.warning(f"Failed to load from {json_path}: {e}")
        else:
            logger.info(f"No existing data found at {json_path}")
    
    def _save_to_json(self):
        """Save embeddings and chunks to JSON file"""
        json_path = self._get_json_path()
        try:
            data = {
                'embeddings': [emb.tolist() for emb in self.embeddings],
                'chunks': self.chunks,
                'metadatas': self.metadatas
            }
            with open(json_path, 'w') as f:
                json.dump(data, f)
            logger.info(f"Saved {len(self.chunks)} chunks to {json_path}")
        except Exception as e:
            logger.error(f"Failed to save to {json_path}: {e}")
    
    def add_chunks(self, chunks: List[Dict], embeddings: List[List[float]]):
        """
        Add chunks with embeddings to the vector store.
        
        Args:
            chunks: List of chunk dictionaries with 'text' and 'metadata'
            embeddings: List of embedding vectors
        """
        if len(chunks) != len(embeddings):
            raise ValueError(f"Mismatch: {len(chunks)} chunks but {len(embeddings)} embeddings")
        
        # Convert to numpy arrays and normalize
        for emb in embeddings:
            emb_array = np.array(emb, dtype=np.float32)
            # Normalize for cosine similarity
            norm = np.linalg.norm(emb_array)
            if norm > 0:
                emb_array = emb_array / norm
            self.embeddings.append(emb_array)
        
        # Store chunks and metadatas
        for chunk in chunks:
            self.chunks.append(chunk.get('text', ''))
            self.metadatas.append(chunk.get('metadata', {}))
        
        # Save to JSON
        self._save_to_json()
        
        logger.info(f"Added {len(chunks)} chunks to vector store")
    
    def search(self, query_embedding: List[float], top_k: int = 3) -> List[Dict]:
        """
        Search for similar chunks using query embedding.
        Uses cosine similarity.
        
        Args:
            query_embedding: Embedding vector of the query
            top_k: Number of results to return
            
        Returns:
            List of dictionaries with 'text', 'metadata', and 'distance'
        """
        if len(self.embeddings) == 0:
            return []
        
        # Convert query to numpy array and normalize
        query_emb = np.array(query_embedding, dtype=np.float32)
        norm = np.linalg.norm(query_emb)
        if norm > 0:
            query_emb = query_emb / norm
        
        # Compute cosine similarities (dot product of normalized vectors)
        similarities = np.array([np.dot(query_emb, emb) for emb in self.embeddings])
        
        # Get top_k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Format results
        retrieved_chunks = []
        for idx in top_indices:
            retrieved_chunks.append({
                "text": self.chunks[idx],
                "metadata": self.metadatas[idx],
                "distance": 1 - similarities[idx]  # Convert similarity to distance
            })
        
        return retrieved_chunks
    
    def get_collection_count(self) -> int:
        """Get number of chunks in collection"""
        return len(self.chunks)
    
    def clear_collection(self):
        """Clear all data from collection"""
        self.embeddings = []
        self.chunks = []
        self.metadatas = []
        
        # Delete JSON file
        json_path = self._get_json_path()
        if os.path.exists(json_path):
            os.remove(json_path)
        
        logger.info("Collection cleared")

