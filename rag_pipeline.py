"""
RAG Pipeline - Main component for Retrieval Augmented Generation
"""

import os
import re
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
        import time
        query_start_time = time.time()
        api_call_count = 0
        
        logger.info(f"Processing query: {query}")
        logger.info("="*70)
        logger.info("STARTING QUERY PROCESSING - Tracking API calls")
        logger.info("="*70)
        
        # Step 1: Generate query embedding (use RETRIEVAL_QUERY task type)
        logger.info("Step 1: Generating query embedding (Expected: 1 Gemini API call)")
        try:
            embedding_start = time.time()
            query_embedding = self.embedder.generate_query_embedding(query)
            api_call_count += 1
            embedding_time = time.time() - embedding_start
            logger.info(f"✓ Step 1: Query embedding generated successfully (API call #{api_call_count}, took {embedding_time:.2f}s)")
        except Exception as e:
            error_str = str(e).lower()
            if "quota" in error_str or "429" in error_str or "limit" in error_str:
                logger.warning(f"Gemini embedding quota exceeded (after {api_call_count} API calls). Switching to local embeddings...")
                # Switch to local embeddings for this query
                self.embedder = LocalEmbeddingGenerator()
                query_embedding = self.embedder.generate_query_embedding(query)
                logger.info("✓ Switched to local embeddings (no API call)")
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
        query_normalized = query_lower.replace("flexicap", "flexi cap").replace("flexi-cap", "flexi cap").replace("flexi cap", "flexi cap")
        
        # Also normalize "elss" variations
        query_normalized = query_normalized.replace("elss tax saver", "elss tax saver fund").replace("elss fund", "elss tax saver fund")
        
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
        
        # Initialize source_urls to avoid UnboundLocalError in exception handler
        source_urls = []
        
        prompt = f"""You are a helpful assistant that answers questions about mutual funds based on provided factual information.

IMPORTANT RULES:
1. Only use information from the provided context
2. Provide factual answers only - NO investment advice
3. Always mention the exact fund name from the context in your answer
4. For returns queries, look for fields like "1 Year Returns", "3 Year Returns", "5 Year Returns", "Returns Since Inception" in the context
5. If the specific fund mentioned in the question is NOT in the context, explicitly state: "The fund [fund name] is not available in the database. This fund may not exist on Groww, the URL may have changed, or the data could not be scraped successfully. Available funds include: ELSS Tax Saver, Conservative Hybrid, Liquid, Arbitrage, Dynamic Asset Allocation, and Long Term Value funds."
6. If the information about the fund exists but the specific field is missing, say: "The [field] for [fund name] is not available in the context."
7. Keep answers concise and factual
8. Do not make up or infer information not explicitly stated
9. Do NOT provide source URLs in your answer - they will be added separately
10. When answering about returns, include the exact percentage values from the context (e.g., "9.49%" or "80.90%")

Context (factual information about mutual funds):
{context}{fund_context_note}

Question: {query}

Answer the question using only the information from the context above. Be factual and concise. Do not provide investment advice. If the fund is not in the context, clearly state that."""

        try:
            logger.info(f"Step 4: Generating answer with Gemini LLM (Expected: 1 Gemini API call, Current total: {api_call_count})")
            logger.info(f"[LLM API] Calling generate_content with prompt length: {len(prompt)} chars")
            llm_start = time.time()
            response = self.llm_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=config_rag.TEMPERATURE,
                    max_output_tokens=config_rag.MAX_TOKENS
                )
            )
            api_call_count += 1
            llm_time = time.time() - llm_start
            
            answer = response.text.strip()
            total_time = time.time() - query_start_time
            logger.info(f"[LLM API] ✓ Success (API call #{api_call_count}, took {llm_time:.2f}s)")
            logger.info("="*70)
            logger.info(f"QUERY COMPLETE - Total API calls: {api_call_count} (Expected: 2), Total time: {total_time:.2f}s")
            logger.info("="*70)
            
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
            
            # Check if answer mentions a fund name from retrieved chunks
            answer_lower = answer.lower()
            answer_mentions_fund = any(
                fund_name.lower() in answer_lower 
                for fund_name in retrieved_fund_names 
                if len(fund_name) > 10
            )
            
            # Determine if the fund itself is not found (vs. just some data missing)
            # Check for explicit "fund not found" patterns, not just "data not available"
            # These patterns indicate the fund itself doesn't exist, not just missing data
            fund_not_found_patterns = [
                "is not available in the database",
                "is not in the database",
                "does not exist",
                "may not exist",
                "not found in the database"
            ]
            
            # Only consider fund not found if answer explicitly says the fund is missing
            # AND doesn't mention a specific fund name from our database
            fund_explicitly_not_found = (
                any(pattern in answer_lower for pattern in fund_not_found_patterns) 
                and not answer_mentions_fund
                and query_fund_name is None
            )
            
            # Include source URLs if:
            # 1. We have retrieved chunks (data was found)
            # 2. Answer mentions a fund name OR we matched a fund from query
            # 3. Fund is not explicitly marked as not found
            should_include_source = (
                len(retrieved_chunks) > 0 
                and (answer_mentions_fund or query_fund_name is not None)
                and not fund_explicitly_not_found
            )
            
            if should_include_source:
                # Determine which fund to use for source URL
                target_fund_name = None
                
                if query_fund_name:
                    # Use the fund matched from query
                    target_fund_name = query_fund_name
                elif answer_mentions_fund:
                    # Find the fund mentioned in the answer
                    for fund_name in retrieved_fund_names:
                        if fund_name.lower() in answer_lower:
                            target_fund_name = fund_name
                            break
                
                # Get source URLs for the target fund
                if target_fund_name:
                    source_urls = list(set([
                        chunk["metadata"].get("source_url", "") 
                        for chunk in retrieved_chunks 
                        if chunk["metadata"].get("fund_name", "").lower() == target_fund_name.lower()
                        and chunk["metadata"].get("source_url")
                    ]))
                else:
                    # Fallback: use all unique source URLs from retrieved chunks
                    source_urls = list(set([
                        chunk["metadata"].get("source_url", "") 
                        for chunk in retrieved_chunks 
                        if chunk["metadata"].get("source_url")
                    ]))
            else:
                # Don't include source URLs if fund wasn't found or no chunks retrieved
                source_urls = []
            
            logger.info("Answer generated successfully using Gemini LLM")
            return {
                "success": True,
                "answer": answer,
                "source_urls": source_urls,
                "query": query,
                "retrieved_chunks": len(retrieved_chunks),
                "mode": "gemini_llm"
            }
            
        except Exception as e:
            error_str = str(e).lower()
            is_quota_error = "quota" in error_str or "429" in error_str or "limit" in error_str
            
            if is_quota_error and retrieved_chunks:
                logger.warning("Gemini API quota exceeded. Using fallback extraction from retrieved chunks.")
                # Fallback: Extract information directly from chunks
                answer = self._extract_answer_from_chunks(query, retrieved_chunks, query_normalized, retrieved_fund_names)
                
                # Get source URLs from retrieved chunks
                source_urls = list(set([
                    chunk["metadata"].get("source_url", "") 
                    for chunk in retrieved_chunks 
                    if chunk["metadata"].get("source_url")
                ]))
                
                logger.info("Using fallback extraction method (Gemini API quota exceeded)")
                return {
                    "success": True,
                    "answer": answer,
                    "source_urls": source_urls,
                    "query": query,
                    "retrieved_chunks": len(retrieved_chunks),
                    "note": "Answer extracted directly from data (LLM quota exceeded)",
                    "mode": "fallback_extraction"
                }
            else:
                logger.error(f"Error generating answer: {e}")
                return {
                    "success": False,
                    "answer": f"Error generating answer: {str(e)}",
                    "source_urls": source_urls,
                    "query": query
                }
    
    def _extract_answer_from_chunks(self, query: str, chunks: List[Dict], query_normalized: str, fund_names: List[str]) -> str:
        """
        Fallback method to extract answers directly from chunks when LLM is unavailable.
        This handles common query patterns like expense ratio, exit load, etc.
        """
        query_lower = query.lower()
        context_text = "\n\n".join([chunk["text"] for chunk in chunks])
        
        # Try to identify the fund name from query
        fund_name = None
        for name in fund_names:
            name_words = set(name.split())
            query_words = set(query_lower.split())
            if len(name_words.intersection(query_words)) >= 2:
                fund_name = name
                break
        
        # Extract common fields
        answer_parts = []
        
        # Check for specific field queries
        if "exit load" in query_lower or "exitload" in query_lower:
            # Look for exit load in context
            exit_load_patterns = [
                r'exit load[:\s]+([^\n]+)',
                r'exitload[:\s]+([^\n]+)',
                r'Exit Load[:\s]+([^\n]+)',
            ]
            for pattern in exit_load_patterns:
                match = re.search(pattern, context_text, re.IGNORECASE)
                if match:
                    exit_load = match.group(1).strip()
                    if fund_name:
                        answer_parts.append(f"The exit load for {fund_name} is {exit_load}.")
                    else:
                        answer_parts.append(f"Exit load: {exit_load}")
                    break
        
        if "expense ratio" in query_lower or "expenseratio" in query_lower:
            expense_patterns = [
                r'expense ratio[:\s]+([^\n]+)',
                r'Expense Ratio[:\s]+([^\n]+)',
                r'Total Expense Ratio[:\s]+([^\n]+)',
            ]
            for pattern in expense_patterns:
                match = re.search(pattern, context_text, re.IGNORECASE)
                if match:
                    expense = match.group(1).strip()
                    if fund_name:
                        answer_parts.append(f"The expense ratio for {fund_name} is {expense}.")
                    else:
                        answer_parts.append(f"Expense ratio: {expense}")
                    break
        
        if "minimum sip" in query_lower or "min sip" in query_lower or "minimum investment" in query_lower:
            sip_patterns = [
                r'minimum sip[:\s]+([^\n]+)',
                r'Minimum SIP[:\s]+([^\n]+)',
                r'minimum investment[:\s]+([^\n]+)',
            ]
            for pattern in sip_patterns:
                match = re.search(pattern, context_text, re.IGNORECASE)
                if match:
                    sip = match.group(1).strip()
                    if fund_name:
                        answer_parts.append(f"The minimum SIP for {fund_name} is {sip}.")
                    else:
                        answer_parts.append(f"Minimum SIP: {sip}")
                    break
        
        if "lock" in query_lower and "in" in query_lower:
            lock_patterns = [
                r'lock[-\s]?in[:\s]+([^\n]+)',
                r'Lock[-\s]?in[:\s]+([^\n]+)',
            ]
            for pattern in lock_patterns:
                match = re.search(pattern, context_text, re.IGNORECASE)
                if match:
                    lock_in = match.group(1).strip()
                    if fund_name:
                        answer_parts.append(f"The lock-in period for {fund_name} is {lock_in}.")
                    else:
                        answer_parts.append(f"Lock-in period: {lock_in}")
                    break
        
        if "riskometer" in query_lower or "risk" in query_lower:
            risk_patterns = [
                r'riskometer[:\s]+([^\n]+)',
                r'Riskometer[:\s]+([^\n]+)',
                r'risk level[:\s]+([^\n]+)',
            ]
            for pattern in risk_patterns:
                match = re.search(pattern, context_text, re.IGNORECASE)
                if match:
                    risk = match.group(1).strip()
                    if fund_name:
                        answer_parts.append(f"The riskometer for {fund_name} is {risk}.")
                    else:
                        answer_parts.append(f"Riskometer: {risk}")
                    break
        
        if "benchmark" in query_lower:
            benchmark_patterns = [
                r'benchmark[:\s]+([^\n]+)',
                r'Benchmark[:\s]+([^\n]+)',
            ]
            for pattern in benchmark_patterns:
                match = re.search(pattern, context_text, re.IGNORECASE)
                if match:
                    benchmark = match.group(1).strip()
                    if fund_name:
                        answer_parts.append(f"The benchmark for {fund_name} is {benchmark}.")
                    else:
                        answer_parts.append(f"Benchmark: {benchmark}")
                    break
        
        # If we found specific information, return it
        if answer_parts:
            answer = " ".join(answer_parts)
            if fund_name:
                # Try to get more context about the fund
                fund_chunks = [c for c in chunks if c["metadata"].get("fund_name", "").lower() == fund_name.lower()]
                if fund_chunks:
                    # Add a note that this is extracted data
                    answer += " (Note: This information was extracted directly from the data due to API quota limits.)"
            return answer
        
        # Fallback: Return relevant context snippets
        if chunks:
            # Get the most relevant chunk (first one is usually most relevant)
            top_chunk = chunks[0]["text"]
            # Extract first few sentences
            sentences = top_chunk.split('.')[:3]
            answer = '. '.join(sentences).strip()
            if answer:
                answer += ". (Note: This is extracted information from the database. For a more detailed answer, please wait for the API quota to reset.)"
                return answer
        
        return "I found relevant information in the database, but I'm unable to generate a detailed answer due to API quota limits. Please try again later or check the source URLs for direct information."
    
    def format_answer(self, response: Dict) -> str:
        """Format the response with source URLs"""
        answer = response.get("answer", "")
        source_urls = response.get("source_urls", [])
        
        if source_urls:
            answer += "\n\nSource: " + source_urls[0]  # Primary source
        
        return answer

