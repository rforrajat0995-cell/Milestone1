"""
Data chunking module for RAG system
Converts structured fund data into text chunks for embedding
"""

from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class FundDataChunker:
    """Chunks mutual fund data into text for RAG"""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def _get_fund_name_variations(self, fund_name: str) -> List[str]:
        """Extract variations of fund name for better search matching"""
        variations = []
        fund_lower = fund_name.lower()
        
        # Extract key terms
        if 'elss' in fund_lower:
            variations.append('ELSS')
            variations.append('ELSS Tax Saver')
            variations.append('ELSS Tax Saver Fund')
        if 'arbitrage' in fund_lower:
            variations.append('Arbitrage')
            variations.append('Arbitrage Fund')
        if 'liquid' in fund_lower:
            variations.append('Liquid')
            variations.append('Liquid Fund')
        if 'conservative hybrid' in fund_lower:
            variations.append('Conservative Hybrid')
            variations.append('Conservative Hybrid Fund')
        if 'dynamic asset allocation' in fund_lower:
            variations.append('Dynamic Asset Allocation')
            variations.append('Dynamic Asset Allocation Fund')
        if 'long term value' in fund_lower:
            variations.append('Long Term Value')
            variations.append('Long Term Value Fund')
        if 'flexi cap' in fund_lower:
            variations.append('Flexi Cap')
            variations.append('Flexi Cap Fund')
        
        # Add Parag Parikh prefix variations
        if 'parag parikh' in fund_lower:
            variations.append('Parag Parikh')
            # Create a copy to avoid modifying list while iterating
            existing_vars = variations[:]
            for var in existing_vars:
                if var and 'parag parikh' not in var.lower():
                    variations.append(f'Parag Parikh {var}')
        
        return list(set(variations))  # Remove duplicates
    
    def create_chunks_from_fund(self, fund_data: Dict) -> List[Dict]:
        """
        Create text chunks from a fund's data.
        Each chunk includes the source URL.
        
        Returns list of chunks with metadata.
        """
        fund_name = fund_data.get("fund_name", "Unknown Fund")
        source_url = fund_data.get("source_url", "")
        
        # Extract fund name variations for better matching
        fund_variations = self._get_fund_name_variations(fund_name)
        
        # Create comprehensive text representation with variations
        text_parts = [
            f"Fund Name: {fund_name}",
        ]
        
        # Add variations if they exist
        if fund_variations:
            text_parts.append(f"Also known as: {', '.join(fund_variations)}")
        
        # Add fund data
        text_parts.extend([
            f"Expense Ratio: {fund_data.get('expense_ratio', 'N/A')}",
            f"Exit Load: {fund_data.get('exit_load', 'N/A')}",
            f"Minimum SIP: {fund_data.get('minimum_sip', 'N/A')}",
            f"Lock-in Period: {fund_data.get('lock_in', 'N/A')}",
            f"Riskometer: {fund_data.get('riskometer', 'N/A')}",
            f"Benchmark: {fund_data.get('benchmark', 'N/A')}"
        ])
        
        # Create main chunk with all information
        main_text = "\n".join(text_parts)
        
        # Create individual field chunks for better retrieval
        chunks = []
        
        # Main comprehensive chunk
        chunks.append({
            "text": main_text,
            "metadata": {
                "fund_name": fund_name,
                "source_url": source_url,
                "chunk_type": "comprehensive",
                "fields": "expense_ratio,exit_load,minimum_sip,lock_in,riskometer,benchmark"  # ChromaDB doesn't support lists
            }
        })
        
        # Individual field chunks for specific queries (also include variations)
        field_variations_text = f"Also known as: {', '.join(fund_variations)}" if fund_variations else ""
        
        field_chunks = [
            {
                "text": f"Fund: {fund_name}\n{field_variations_text}\nExpense Ratio: {fund_data.get('expense_ratio', 'N/A')}" if field_variations_text else f"Fund: {fund_name}\nExpense Ratio: {fund_data.get('expense_ratio', 'N/A')}",
                "metadata": {
                    "fund_name": fund_name,
                    "source_url": source_url,
                    "chunk_type": "field",
                    "field": "expense_ratio"
                }
            },
            {
                "text": f"Fund: {fund_name}\n{field_variations_text}\nExit Load: {fund_data.get('exit_load', 'N/A')}" if field_variations_text else f"Fund: {fund_name}\nExit Load: {fund_data.get('exit_load', 'N/A')}",
                "metadata": {
                    "fund_name": fund_name,
                    "source_url": source_url,
                    "chunk_type": "field",
                    "field": "exit_load"
                }
            },
            {
                "text": f"Fund: {fund_name}\n{field_variations_text}\nMinimum SIP: {fund_data.get('minimum_sip', 'N/A')}" if field_variations_text else f"Fund: {fund_name}\nMinimum SIP: {fund_data.get('minimum_sip', 'N/A')}",
                "metadata": {
                    "fund_name": fund_name,
                    "source_url": source_url,
                    "chunk_type": "field",
                    "field": "minimum_sip"
                }
            },
            {
                "text": f"Fund: {fund_name}\n{field_variations_text}\nLock-in Period: {fund_data.get('lock_in', 'N/A')}" if field_variations_text else f"Fund: {fund_name}\nLock-in Period: {fund_data.get('lock_in', 'N/A')}",
                "metadata": {
                    "fund_name": fund_name,
                    "source_url": source_url,
                    "chunk_type": "field",
                    "field": "lock_in"
                }
            },
            {
                "text": f"Fund: {fund_name}\n{field_variations_text}\nRiskometer (Risk Factor): {fund_data.get('riskometer', 'N/A')}" if field_variations_text else f"Fund: {fund_name}\nRiskometer (Risk Factor): {fund_data.get('riskometer', 'N/A')}",
                "metadata": {
                    "fund_name": fund_name,
                    "source_url": source_url,
                    "chunk_type": "field",
                    "field": "riskometer"
                }
            },
            {
                "text": f"Fund: {fund_name}\n{field_variations_text}\nBenchmark: {fund_data.get('benchmark', 'N/A')}" if field_variations_text else f"Fund: {fund_name}\nBenchmark: {fund_data.get('benchmark', 'N/A')}",
                "metadata": {
                    "fund_name": fund_name,
                    "source_url": source_url,
                    "chunk_type": "field",
                    "field": "benchmark"
                }
            }
        ]
        
        chunks.extend(field_chunks)
        
        return chunks
    
    def create_chunks_from_all_funds(self, funds_data: Dict) -> List[Dict]:
        """
        Create chunks from all funds in the database.
        
        Args:
            funds_data: Dictionary with 'funds' key containing fund data
            
        Returns:
            List of all chunks with metadata
        """
        all_chunks = []
        funds = funds_data.get("funds", {})
        
        for fund_name, fund_data in funds.items():
            chunks = self.create_chunks_from_fund(fund_data)
            all_chunks.extend(chunks)
            logger.info(f"Created {len(chunks)} chunks for {fund_name}")
        
        logger.info(f"Total chunks created: {len(all_chunks)}")
        return all_chunks
