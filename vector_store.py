"""
Vector store for RAG system
Uses ChromaDB for persistent vector storage
"""

import os
from typing import List, Dict, Optional
import logging

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    logging.warning("ChromaDB not installed. Run: pip install chromadb")

logger = logging.getLogger(__name__)


class VectorStore:
    """Vector database for storing and retrieving embeddings"""
    
    def __init__(self, db_path: str = "data/vector_db", collection_name: str = "mutual_funds"):
        if not CHROMA_AVAILABLE:
            raise ImportError("ChromaDB required. Install with: pip install chromadb")
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection_name = collection_name
        self.collection = self._get_or_create_collection()
    
    def _get_or_create_collection(self):
        """Get existing collection or create new one"""
        try:
            collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Loaded existing collection: {self.collection_name}")
            return collection
        except:
            collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Mutual fund data for RAG"}
            )
            logger.info(f"Created new collection: {self.collection_name}")
            return collection
    
    def add_chunks(self, chunks: List[Dict], embeddings: List[List[float]]):
        """
        Add chunks with embeddings to the vector store.
        
        Args:
            chunks: List of chunk dictionaries with 'text' and 'metadata'
            embeddings: List of embedding vectors
        """
        if len(chunks) != len(embeddings):
            raise ValueError(f"Mismatch: {len(chunks)} chunks but {len(embeddings)} embeddings")
        
        # Prepare data for ChromaDB
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        texts = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        
        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
        
        logger.info(f"Added {len(chunks)} chunks to vector store")
    
    def search(self, query_embedding: List[float], top_k: int = 3) -> List[Dict]:
        """
        Search for similar chunks using query embedding.
        
        Args:
            query_embedding: Embedding vector of the query
            top_k: Number of results to return
            
        Returns:
            List of dictionaries with 'text', 'metadata', and 'distance'
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        # Format results
        retrieved_chunks = []
        if results['documents'] and len(results['documents'][0]) > 0:
            for i in range(len(results['documents'][0])):
                retrieved_chunks.append({
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if 'distances' in results else None
                })
        
        return retrieved_chunks
    
    def get_collection_count(self) -> int:
        """Get number of chunks in collection"""
        return self.collection.count()
    
    def clear_collection(self):
        """Clear all data from collection"""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self._get_or_create_collection()
            logger.info("Collection cleared")
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")

