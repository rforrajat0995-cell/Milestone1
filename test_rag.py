"""
Test script for RAG system
Tests the query: "Tell me the exit load for Parag Parikh Liquid Fund Direct Growth?"
"""

import os
import sys
from rag_pipeline import RAGPipeline
import config_rag

def main():
    """Test the RAG system"""
    print("="*70)
    print("RAG SYSTEM TEST")
    print("="*70)
    
    # Check for API key
    api_key = os.getenv("GOOGLE_API_KEY") or config_rag.GOOGLE_API_KEY
    if not api_key:
        print("\n❌ ERROR: Google API key not found!")
        print("\nPlease set your API key in .env file or environment variable")
        print("Get your API key from: https://aistudio.google.com/app/apikey")
        sys.exit(1)
    
    try:
        # Initialize RAG pipeline
        print("\n1. Initializing RAG pipeline...")
        # Use local embeddings (since API quota is exceeded)
        pipeline = RAGPipeline(api_key=api_key, use_local_embeddings=True)
        
        # Check if index exists
        chunk_count = pipeline.vector_store.get_collection_count()
        if chunk_count == 0:
            print("\n⚠️  Vector index is empty!")
            print("   Please run: python build_rag_index.py")
            sys.exit(1)
        
        print(f"   ✓ Vector index loaded ({chunk_count} chunks)")
        print(f"   ✓ Using LLM: {config_rag.GEMINI_LLM_MODEL}\n")
        
        # Test query
        test_query = "Tell me the exit load for Parag Parikh Liquid Fund Direct Growth?"
        
        print("2. Processing query:")
        print(f"   Query: {test_query}\n")
        
        # Get answer
        response = pipeline.answer_query(test_query)
        
        # Display result
        print("3. Response:")
        print("-"*70)
        formatted = pipeline.format_answer(response)
        print(formatted)
        print("-"*70)
        
        if response.get("success"):
            print("\n✅ SUCCESS!")
            print(f"   Retrieved chunks: {response.get('retrieved_chunks', 0)}")
            print(f"   Source URLs: {len(response.get('source_urls', []))}")
            if response.get('source_urls'):
                print(f"   Primary source: {response['source_urls'][0]}")
        else:
            print(f"\n❌ FAILED: {response.get('answer')}")
        
        print("\n" + "="*70)
        
        # Test additional queries
        print("\n4. Testing additional queries:\n")
        additional_queries = [
            "What is the expense ratio of Parag Parikh ELSS Tax Saver Fund?",
            "Tell me the riskometer for Parag Parikh Arbitrage Fund",
            "What is the minimum SIP for Parag Parikh Liquid Fund?"
        ]
        
        for q in additional_queries:
            print(f"   Query: {q}")
            resp = pipeline.answer_query(q)
            if resp.get('success'):
                print(f"   ✓ {resp['answer'][:100]}...")
                if resp.get('source_urls'):
                    print(f"   Source: {resp['source_urls'][0]}")
            else:
                print(f"   ✗ {resp.get('answer', 'Error')}")
            print()
        
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

