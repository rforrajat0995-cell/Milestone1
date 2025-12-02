"""
Query handler for answering questions about mutual funds
Backend component that processes queries and returns answers with source URLs
"""

import re
from typing import Dict, Optional, List
import logging

from data_storage import DataStorage

logger = logging.getLogger(__name__)


class QueryHandler:
    """Handles queries about mutual fund data"""
    
    def __init__(self, storage: DataStorage = None):
        self.storage = storage or DataStorage()
        
        # Field mappings for natural language queries
        self.field_keywords = {
            "expense_ratio": ["expense ratio", "expense", "er", "total expense ratio"],
            "exit_load": ["exit load", "exit", "load", "redemption charge"],
            "minimum_sip": ["minimum sip", "min sip", "sip minimum", "minimum investment"],
            "lock_in": ["lock in", "lock-in", "lockin", "lock period", "lock"],
            "riskometer": ["riskometer", "risk", "risk factor", "risk level", "risk rating"],
            "benchmark": ["benchmark", "index", "benchmark index"]
        }
    
    def parse_query(self, query: str) -> Dict:
        """
        Parse a natural language query to extract:
        - Fund name
        - Field of interest
        """
        query_lower = query.lower()
        
        # Extract fund name (look for "Parag Parikh" funds)
        fund_name = self._extract_fund_name(query)
        
        # Extract field of interest
        field = self._extract_field(query_lower)
        
        return {
            "fund_name": fund_name,
            "field": field,
            "original_query": query
        }
    
    def _extract_fund_name(self, query: str) -> Optional[str]:
        """Extract fund name from query"""
        query_lower = query.lower()
        
        # Check if "Parag Parikh" is mentioned
        if "parag parikh" not in query_lower:
            return None
        
        # Extract the fund type/name part
        # Pattern: "Parag Parikh" followed by fund name until question mark or end
        pattern = r"parag\s+parikh\s+([^?]+?)(?:\?|$|for|about|the|is)"
        match = re.search(pattern, query, re.IGNORECASE)
        
        if match:
            fund_part = match.group(1).strip()
            
            # Check if "Direct Growth" is already in the extracted part
            has_direct_growth = "direct growth" in fund_part.lower()
            
            # Remove trailing words carefully - don't remove if "Direct Growth" is present
            if not has_direct_growth:
                fund_part = re.sub(r'\s+(fund)\s*$', '', fund_part, flags=re.IGNORECASE)
            else:
                # If "Direct Growth" is present, just clean up extra "Fund" if any
                fund_part = re.sub(r'\s+(fund)\s+(direct growth)', r' \2', fund_part, flags=re.IGNORECASE)
            
            fund_part = fund_part.strip()
            
            # Reconstruct full name properly
            if not fund_part:
                return None
            
            # Check if it already contains "Parag Parikh"
            if "parag parikh" not in fund_part.lower():
                fund_name = f"Parag Parikh {fund_part}"
            else:
                fund_name = fund_part
            
            # Ensure "Direct Growth" is at the end if not already present
            if "direct growth" not in fund_name.lower():
                fund_name = f"{fund_name} Direct Growth"
            
            return fund_name
        
        return None
    
    def _extract_field(self, query_lower: str) -> Optional[str]:
        """Extract field of interest from query"""
        # Check for field keywords in order of specificity (longer/more specific first)
        # Sort by keyword length (longest first) to match most specific terms first
        field_matches = []
        for field, keywords in self.field_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    field_matches.append((len(keyword), field, keyword))
        
        if field_matches:
            # Sort by length (longest first) and return the most specific match
            field_matches.sort(reverse=True, key=lambda x: x[0])
            return field_matches[0][1]
        
        return None
    
    def answer_query(self, query: str) -> Dict:
        """
        Answer a query about mutual fund data.
        Returns answer with source URL.
        
        Example: "Tell me the exit load for Parag Parikh Liquid Fund Direct Growth?"
        """
        logger.info(f"Processing query: {query}")
        
        # Parse the query
        parsed = self.parse_query(query)
        fund_name = parsed["fund_name"]
        field = parsed["field"]
        
        if not fund_name:
            return {
                "success": False,
                "answer": "I couldn't identify which fund you're asking about. Please specify the fund name.",
                "source_url": None
            }
        
        if not field:
            return {
                "success": False,
                "answer": f"I found the fund '{fund_name}', but couldn't identify what information you need. Please specify: expense ratio, exit load, minimum SIP, lock-in, riskometer, or benchmark.",
                "source_url": None
            }
        
        # Get the data
        result = self.storage.get_field_value(fund_name, field)
        
        if not result:
            # Try to find the fund with fuzzy matching
            fund_data = self.storage.get_fund_by_name(fund_name)
            if fund_data:
                # Fund found but field might be missing
                return {
                    "success": False,
                    "answer": f"I found the fund '{fund_data['fund_name']}', but the {field.replace('_', ' ')} information is not available in our database.",
                    "source_url": fund_data.get("source_url")
                }
            else:
                return {
                    "success": False,
                    "answer": f"I couldn't find the fund '{fund_name}' in our database. Please check the fund name and try again.",
                    "source_url": None
                }
        
        # Format the answer
        field_display = field.replace("_", " ").title()
        answer = f"The {field_display} for {result['fund_name']} is {result['value']}."
        
        return {
            "success": True,
            "answer": answer,
            "fund_name": result["fund_name"],
            "field": field,
            "value": result["value"],
            "source_url": result["source_url"],
            "query": query
        }
    
    def get_fund_info(self, fund_name: str) -> Optional[Dict]:
        """Get all information about a fund"""
        return self.storage.get_fund_by_name(fund_name)


def format_answer(response: Dict) -> str:
    """Format the response for display"""
    if not response.get("success"):
        return response.get("answer", "Sorry, I couldn't process your query.")
    
    answer = response.get("answer", "")
    source_url = response.get("source_url")
    
    if source_url:
        answer += f"\n\nSource: {source_url}"
    
    return answer


def main():
    """Test the query handler"""
    print("="*70)
    print("QUERY HANDLER TEST")
    print("="*70)
    
    # Initialize
    storage = DataStorage()
    handler = QueryHandler(storage)
    
    # Test query
    test_query = "Tell me the exit load for Parag Parikh Liquid Fund Direct Growth?"
    
    print(f"\nQuery: {test_query}\n")
    
    # Process query
    response = handler.answer_query(test_query)
    
    # Display result
    print("Response:")
    print("-"*70)
    print(format_answer(response))
    print("-"*70)
    
    if response.get("success"):
        print(f"\n✓ Successfully answered query")
        print(f"  Fund: {response.get('fund_name')}")
        print(f"  Field: {response.get('field')}")
        print(f"  Value: {response.get('value')}")
        print(f"  Source: {response.get('source_url')}")
    else:
        print(f"\n✗ Failed to answer query")
        print(f"  Reason: {response.get('answer')}")


if __name__ == "__main__":
    main()

