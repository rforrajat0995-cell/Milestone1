"""
Test RAG system with user's specific query
"""

import os
import sys
from rag_pipeline import RAGPipeline
import config_rag

def test_query():
    """Test the user's query"""
    query = "What is the risk factor of Parag Parikh Conservative Hybrid Fund Direct Growth? Should I invest in it for a long term?"
    
    print("="*70)
    print("RAG SYSTEM TEST - USER QUERY")
    print("="*70)
    print(f"\nQuery: {query}\n")
    
    # Check for API key
    api_key = os.getenv("GOOGLE_API_KEY") or config_rag.GOOGLE_API_KEY
    if not api_key:
        print("\n❌ ERROR: Google API key not found!")
        sys.exit(1)
    
    try:
        # Initialize RAG pipeline
        print("Initializing RAG pipeline...")
        pipeline = RAGPipeline(api_key=api_key, use_local_embeddings=True)
        
        # Check if index exists
        chunk_count = pipeline.vector_store.get_collection_count()
        if chunk_count == 0:
            print("\n⚠️  Vector index is empty!")
            print("   Please run: python build_rag_index.py")
            sys.exit(1)
        
        print(f"✓ Vector index loaded ({chunk_count} chunks)")
        print(f"✓ Using LLM: {config_rag.GEMINI_LLM_MODEL}\n")
        
        # Process query
        print("Processing query through RAG pipeline...\n")
        response = pipeline.answer_query(query)
        
        # Display result
        print("="*70)
        print("RAG SYSTEM RESPONSE")
        print("="*70)
        formatted = pipeline.format_answer(response)
        print(formatted)
        print("="*70)
        
        if response.get("success"):
            print("\n✅ SUCCESS!")
            print(f"   Retrieved chunks: {response.get('retrieved_chunks', 0)}")
            print(f"   Source URLs: {len(response.get('source_urls', []))}")
            if response.get('source_urls'):
                print(f"   Primary source: {response['source_urls'][0]}")
            
            # Check answer quality
            answer = response.get('answer', '').lower()
            print("\n" + "-"*70)
            print("ANSWER ANALYSIS:")
            print("-"*70)
            
            # Check for risk factor answer
            if 'risk' in answer or 'riskometer' in answer:
                print("✓ Risk factor question addressed")
            else:
                print("⚠ Risk factor not clearly mentioned")
            
            # Check for investment advice refusal
            advice_keywords = ['should i invest', 'investment advice', 'cannot provide', 'not provide advice', 
                             'no investment advice', 'factual information', 'not advice', 'cannot recommend']
            has_advice_refusal = any(keyword in answer for keyword in advice_keywords)
            
            if has_advice_refusal:
                print("✓ Investment advice properly refused")
            else:
                print("⚠ Investment advice refusal not clearly stated")
        else:
            print(f"\n❌ FAILED: {response.get('answer')}")
        
        print("\n" + "="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    test_query()

