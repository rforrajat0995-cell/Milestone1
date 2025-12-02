"""
Script to build the RAG vector index from stored fund data
Run this after collecting data and before answering queries
"""

import os
import sys
from rag_pipeline import RAGPipeline
import config_rag

def main():
    """Build the RAG index"""
    print("="*70)
    print("BUILDING RAG VECTOR INDEX")
    print("="*70)
    
    # Check for API key
    api_key = os.getenv("GOOGLE_API_KEY") or config_rag.GOOGLE_API_KEY
    if not api_key:
        print("\n❌ ERROR: Google API key not found!")
        print("\nPlease set your API key:")
        print("  1. Create a .env file in the project root")
        print("  2. Add: GOOGLE_API_KEY=your_api_key_here")
        print("  3. Or set environment variable: export GOOGLE_API_KEY=your_key")
        print("\nYou can get an API key from: https://aistudio.google.com/app/apikey")
        sys.exit(1)
    
    print(f"\n✓ API key found")
    print(f"✓ Using embedding model: {config_rag.GEMINI_EMBEDDING_MODEL}")
    print(f"✓ Vector DB path: {config_rag.VECTOR_DB_PATH}\n")
    
    try:
        # Initialize RAG pipeline
        print("Initializing RAG pipeline...")
        pipeline = RAGPipeline(api_key=api_key, use_local_embeddings=False)
        
        # Build index
        print("\nBuilding vector index from fund data...")
        try:
            chunk_count = pipeline.build_index()
        except Exception as e:
            error_str = str(e).lower()
            if "quota" in error_str or "429" in error_str or "limit: 0" in error_str:
                print("\n⚠️  API quota exceeded for embeddings. Switching to local embeddings (no API needed)...")
                # Reinitialize with local embeddings
                pipeline = RAGPipeline(api_key=api_key, use_local_embeddings=True)
                chunk_count = pipeline.build_index()
            else:
                raise
        
        print("\n" + "="*70)
        print("✅ INDEX BUILT SUCCESSFULLY")
        print("="*70)
        print(f"Total chunks indexed: {chunk_count}")
        print(f"Vector DB location: {config_rag.VECTOR_DB_PATH}")
        print("\nYou can now use the RAG system to answer queries!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

