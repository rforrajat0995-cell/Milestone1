"""
Script to fix database format and rebuild RAG index
"""

import os
from data_storage import DataStorage
from rag_pipeline import RAGPipeline
import config_rag

def main():
    print("="*70)
    print("FIXING DATABASE AND REBUILDING RAG INDEX")
    print("="*70)
    
    # Step 1: Fix database format
    print("\n1. Fixing database format...")
    storage = DataStorage()
    data = storage.load_data()
    
    if data:
        print(f"   ✓ Database loaded: {len(data.get('funds', {}))} funds")
        # Save again to ensure format is correct
        storage.save_data(data)
        print("   ✓ Database format normalized")
    else:
        print("   ⚠️  No data found in database")
        return
    
    # Step 2: Rebuild RAG index
    print("\n2. Rebuilding RAG index...")
    api_key = os.getenv("GOOGLE_API_KEY") or config_rag.GOOGLE_API_KEY
    
    try:
        pipeline = RAGPipeline(api_key=api_key, use_local_embeddings=True)
        chunk_count = pipeline.build_index()
        print(f"   ✓ Index rebuilt with {chunk_count} chunks")
    except Exception as e:
        print(f"   ❌ Error rebuilding index: {e}")
        return
    
    # Step 3: Test queries
    print("\n3. Testing queries...")
    test_queries = [
        "What is the exit load for ELSS?",
        "What is the risk factor for Parag Parikh Liquid Fund?",
        "What is the riskometer for flexicap fund?"
    ]
    
    for query in test_queries:
        response = pipeline.answer_query(query)
        print(f"\n   Query: {query}")
        print(f"   Answer: {response.get('answer', '')[:80]}...")
        print(f"   Source URLs: {len(response.get('source_urls', []))} URLs")
    
    print("\n" + "="*70)
    print("✅ COMPLETE!")
    print("="*70)
    print("\nNext steps:")
    print("1. Restart the backend server: python backend_rag_api.py")
    print("2. Test queries in the frontend")
    print("="*70)

if __name__ == "__main__":
    main()

