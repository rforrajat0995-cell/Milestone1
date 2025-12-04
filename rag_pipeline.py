"""
RAG Pipeline - Main component for Retrieval Augmented Generation
"""

import os
from typing import Dict, List, Optional
import logging

from data_storage import DataStorage
from data_chunking import FundDataChunker
from embeddings import EmbeddingGenerator
from embeddings_local import LocalEmbeddingGenerator
import config_rag

# Use simple vector store for Vercel (lighter than ChromaDB)
try:
    from vector_store_simple import SimpleVectorStore as VectorStore
    SIMPLE_VECTOR_STORE = True
except ImportError:
    from vector_store import VectorStore
    SIMPLE_VECTOR_STORE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

logger = logging.getLogger(__name__)


class RAGPipeline:
    """Complete RAG pipeline for answering queries"""
    
    def __init__(self, api_key: Optional[str] = None, use_local_embeddings: bool = False):
        # Initialize components
        self.storage = DataStorage()
        self.chunker = FundDataChunker(
            chunk_size=config_rag.CHUNK_SIZE,
            chunk_overlap=config_rag.CHUNK_OVERLAP
        )
        
        # Initialize embeddings
        if use_local_embeddings:
            logger.info("Using local embeddings (sentence-transformers)")
            self.embedder = LocalEmbeddingGenerator()
        else:
            # Try Google Gemini embeddings
            api_key = api_key or config_rag.GOOGLE_API_KEY
            if not api_key:
                logger.warning("No API key found. Falling back to local embeddings.")
                self.embedder = LocalEmbeddingGenerator()
                use_local_embeddings = True
            else:
                try:
                    self.embedder = EmbeddingGenerator(api_key=api_key, model=config_rag.GEMINI_EMBEDDING_MODEL)
                    logger.info("Using Google Gemini embeddings")
                except Exception as e:
                    logger.warning(f"Failed to initialize Gemini embeddings: {e}. Falling back to local embeddings.")
                    self.embedder = LocalEmbeddingGenerator()
                    use_local_embeddings = True
        
        self.vector_store = VectorStore(db_path=config_rag.VECTOR_DB_PATH)
        
        # Initialize Gemini LLM (still needed for answer generation)
        api_key = api_key or config_rag.GOOGLE_API_KEY
        if not api_key:
            raise ValueError("Google API key required for LLM. Set GOOGLE_API_KEY environment variable.")
        
        if not GEMINI_AVAILABLE:
            raise ImportError("Google Generative AI library required. Install with: pip install google-generativeai")
        genai.configure(api_key=api_key)
        self.llm_model = genai.GenerativeModel(config_rag.GEMINI_LLM_MODEL)
    
    def build_index(self):
        """
        Build the vector index from stored fund data.
        This should be run once after data collection.
        """
        logger.info("Building vector index...")
        
        # Load fund data
        funds_data = self.storage.load_data()
        if not funds_data:
            raise ValueError("No fund data found. Run data_storage.py first to collect data.")
        
        # Ensure consistent dict format with "funds" key
        if isinstance(funds_data, list):
            # Convert list format to dict format
            funds_dict = {}
            for fund in funds_data:
                if fund.get("validation_status") == "valid":
                    funds_dict[fund.get("fund_name")] = fund
            funds_data = {"funds": funds_dict}
        elif isinstance(funds_data, dict) and "funds" not in funds_data:
            # If it's a dict but not in expected format, try to convert
            funds_data = {"funds": funds_data}
        
        # Filter to only valid funds (only index funds with valid data)
        if "funds" in funds_data:
            valid_funds = {}
            invalid_funds = {}
            
            for name, fund in funds_data["funds"].items():
                if fund.get("validation_status") == "valid":
                    valid_funds[name] = fund
                else:
                    invalid_funds[name] = fund
            
            funds_data["funds"] = valid_funds
            logger.info(f"Filtered to {len(valid_funds)} valid funds for indexing")
            if invalid_funds:
                logger.info(f"Skipped {len(invalid_funds)} invalid/failed funds: {list(invalid_funds.keys())}")
        
        # Check if index already exists
        if self.vector_store.get_collection_count() > 0:
            logger.warning("Vector index already exists. Clearing and rebuilding...")
            self.vector_store.clear_collection()
        
        # Create chunks
        chunks = self.chunker.create_chunks_from_all_funds(funds_data)
        
        # Generate embeddings
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.embedder.generate_embeddings_batch(texts)
        
        # Store in vector database
        self.vector_store.add_chunks(chunks, embeddings)
        
        logger.info(f"Index built successfully with {len(chunks)} chunks")
        return len(chunks)
    
    def answer_query(self, query: str) -> Dict:
        """
        Answer a query using RAG pipeline.
        
        Args:
            query: Natural language query
            
        Returns:
            Dictionary with answer, source URLs, and metadata
        """
        logger.info(f"Processing query: {query}")
        
        # Step 1: Generate query embedding (use RETRIEVAL_QUERY task type)
        try:
            query_embedding = self.embedder.generate_query_embedding(query)
        except Exception as e:
            error_str = str(e).lower()
            if "quota" in error_str or "429" in error_str or "limit" in error_str:
                logger.warning("Gemini embedding quota exceeded during query. Switching to local embeddings...")
                # Switch to local embeddings for this query
                self.embedder = LocalEmbeddingGenerator()
                query_embedding = self.embedder.generate_query_embedding(query)
            else:
                raise
        
        # Step 2: Retrieve relevant chunks
        retrieved_chunks = self.vector_store.search(
            query_embedding,
            top_k=config_rag.TOP_K_RETRIEVAL
        )
        
        if not retrieved_chunks:
            return {
                "success": False,
                "answer": "I couldn't find relevant information to answer your query.",
                "source_urls": [],
                "query": query
            }
        
        # Step 3: Prepare context for LLM
        context = "\n\n".join([chunk["text"] for chunk in retrieved_chunks])
        
        # Normalize query for better matching (handle variations like "flexicap" vs "flexi cap")
        query_lower = query.lower()
        query_normalized = query_lower.replace("flexicap", "flexi cap").replace("flexi-cap", "flexi cap")
        
        retrieved_fund_names = [chunk["metadata"].get("fund_name", "").lower() for chunk in retrieved_chunks]
        
        # Check if query mentions a fund that might exist but isn't in context
        from data_storage import DataStorage
        storage = DataStorage()
        all_funds_data = storage.load_data()
        
        # Normalize to get all fund names
        all_fund_names = []
        if isinstance(all_funds_data, list):
            all_fund_names = [f.get("fund_name", "") for f in all_funds_data]
        elif isinstance(all_funds_data, dict) and "funds" in all_funds_data:
            all_fund_names = list(all_funds_data["funds"].keys())
        elif isinstance(all_funds_data, dict):
            all_fund_names = list(all_funds_data.keys())
        
        # Check if query mentions a fund that exists but isn't in retrieved chunks
        query_fund_mentioned = None
        query_lower_words = set(query_lower.split())
        for fund_name in all_fund_names:
            fund_words = set(fund_name.lower().split())
            if len(query_lower_words.intersection(fund_words)) >= 3:  # At least 3 matching words
                # Check if this fund is in retrieved chunks
                if not any(fund_name.lower() == chunk["metadata"].get("fund_name", "").lower() 
                          for chunk in retrieved_chunks):
                    query_fund_mentioned = fund_name
                    break
        
        # Step 4: Generate answer using Gemini LLM
        fund_context_note = ""
        if query_fund_mentioned:
            fund_context_note = f"\n\nNOTE: The fund '{query_fund_mentioned}' exists in the database but has no valid data (scraping failed or data unavailable)."
        
        prompt = f"""You are a helpful assistant that answers questions about mutual funds based on provided factual information.

IMPORTANT RULES:
1. Only use information from the provided context
2. Provide factual answers only - NO investment advice
3. Always mention the exact fund name from the context in your answer
4. If the specific fund mentioned in the question is NOT in the context, explicitly state: "The fund [fund name] is not available in the database. This fund may not exist on Groww, the URL may have changed, or the data could not be scraped successfully. Available funds include: ELSS Tax Saver, Conservative Hybrid, Liquid, Arbitrage, Dynamic Asset Allocation, and Long Term Value funds."
5. If the information about the fund exists but the specific field is missing, say: "The [field] for [fund name] is not available in the context."
6. Keep answers concise and factual
7. Do not make up or infer information not explicitly stated
8. Do NOT provide source URLs in your answer - they will be added separately

Context (factual information about mutual funds):
{context}{fund_context_note}

Question: {query}

Answer the question using only the information from the context above. Be factual and concise. Do not provide investment advice. If the fund is not in the context, clearly state that."""

        try:
            response = self.llm_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=config_rag.TEMPERATURE,
                    max_output_tokens=config_rag.MAX_TOKENS
                )
            )
            
            answer = response.text.strip()
            
            # Only include source URLs if the answer indicates the information was found
            # Check if answer says fund is not available
            answer_lower = answer.lower()
            fund_not_found_indicators = [
                "not available",
                "not in the context",
                "not in the database",
                "is not available",
                "not found",
                "does not exist"
            ]
            
            # Extract fund name from query - try to match with retrieved chunks
            query_fund_name = None
            query_words = set([w for w in query_normalized.split() if len(w) > 3])
            
            # Try to find matching fund in retrieved chunks
            best_match_score = 0
            for fund_name in retrieved_fund_names:
                fund_words = set([w for w in fund_name.split() if len(w) > 3])
                # Calculate match score
                match_score = len(query_words.intersection(fund_words))
                if match_score > best_match_score and match_score >= 2:  # Need at least 2 matching words
                    best_match_score = match_score
                    query_fund_name = fund_name
            
            # Check if answer indicates fund was found (mentions a fund name from context)
            answer_mentions_fund = any(
                fund_name in answer_lower 
                for fund_name in retrieved_fund_names 
                if len(fund_name) > 10
            )
            
            # Determine if fund was found
            fund_not_found = any(indicator in answer_lower for indicator in fund_not_found_indicators)
            fund_found = not fund_not_found and (answer_mentions_fund or query_fund_name is not None)
            
            if fund_found:
                if query_fund_name:
                    # Only include source URLs from chunks that match the query fund name
                    source_urls = list(set([
                        chunk["metadata"].get("source_url", "") 
                        for chunk in retrieved_chunks 
                        if chunk["metadata"].get("fund_name", "").lower() == query_fund_name
                        and chunk["metadata"].get("source_url")
                    ]))
                else:
                    # If we can't match exactly, but answer mentions a fund, use that fund's URL
                    # Find the fund mentioned in the answer
                    mentioned_fund = None
                    for fund_name in retrieved_fund_names:
                        if fund_name in answer_lower:
                            mentioned_fund = fund_name
                            break
                    
                    if mentioned_fund:
                        source_urls = list(set([
                            chunk["metadata"].get("source_url", "") 
                            for chunk in retrieved_chunks 
                            if chunk["metadata"].get("fund_name", "").lower() == mentioned_fund
                            and chunk["metadata"].get("source_url")
                        ]))
                    else:
                        # Fallback: use all source URLs if we can't determine
                        source_urls = list(set([chunk["metadata"].get("source_url", "") for chunk in retrieved_chunks if chunk["metadata"].get("source_url")]))
            else:
                # Don't include source URLs if the fund wasn't found
                source_urls = []
            
            return {
                "success": True,
                "answer": answer,
                "source_urls": source_urls,
                "query": query,
                "retrieved_chunks": len(retrieved_chunks)
            }
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return {
                "success": False,
                "answer": f"Error generating answer: {str(e)}",
                "source_urls": source_urls,
                "query": query
            }
    
    def format_answer(self, response: Dict) -> str:
        """Format the response with source URLs"""
        answer = response.get("answer", "")
        source_urls = response.get("source_urls", [])
        
        if source_urls:
            answer += "\n\nSource: " + source_urls[0]  # Primary source
        
        return answer

