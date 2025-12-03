"""
Data storage module for storing scraped mutual fund data
Follows the recommended architecture: precompute and store with source URLs
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Only import scraper when actually needed (not in API functions)
try:
    from scraper import GrowwMFScraper
    import config
    SCRAPER_AVAILABLE = True
except ImportError:
    SCRAPER_AVAILABLE = False
    # Scraper not needed in API functions

logger = logging.getLogger(__name__)


class DataStorage:
    """Handles storage and retrieval of mutual fund data"""
    
    def __init__(self, storage_dir: str = "data/storage"):
        self.storage_dir = storage_dir
        self.funds_file = os.path.join(storage_dir, "funds_database.json")
        self.ensure_storage_directory()
    
    def ensure_storage_directory(self):
        """Create storage directory if it doesn't exist"""
        os.makedirs(self.storage_dir, exist_ok=True)
    
    def scrape_and_store_all_funds(self) -> Dict:
        """
        Scrape all funds and store the data.
        Returns summary of the operation.
        """
        logger.info("Starting data collection for all Parag Parikh funds")
        
        if not SCRAPER_AVAILABLE:
            raise ImportError("Scraper dependencies not available. Install: pip install beautifulsoup4 lxml requests")
        scraper = GrowwMFScraper()
        results = scraper.scrape_all_funds()
        
        # Prepare data for storage
        storage_data = {
            "metadata": {
                "scraped_at": datetime.now().isoformat(),
                "total_funds": len(results),
                "source": "groww.in",
                "amc": "Parag Parikh AMC"
            },
            "funds": {}
        }
        
        # Organize by fund name for easy lookup
        valid_count = 0
        invalid_count = 0
        
        for fund_data in results:
            fund_name = fund_data.get("fund_name", "Unknown")
            
            # Only store valid data
            if fund_data.get("validation_status") == "valid":
                storage_data["funds"][fund_name] = {
                    "fund_name": fund_name,
                    "source_url": fund_data.get("source_url"),
                    "expense_ratio": fund_data.get("expense_ratio"),
                    "exit_load": fund_data.get("exit_load"),
                    "minimum_sip": fund_data.get("minimum_sip"),
                    "lock_in": fund_data.get("lock_in"),
                    "riskometer": fund_data.get("riskometer"),
                    "benchmark": fund_data.get("benchmark"),
                    "scraped_at": fund_data.get("scraped_at", datetime.now().isoformat()),
                    "validation_status": "valid"
                }
                valid_count += 1
            else:
                logger.warning(f"Skipping invalid data for {fund_name}")
                invalid_count += 1
        
        storage_data["metadata"]["valid_funds"] = valid_count
        storage_data["metadata"]["invalid_funds"] = invalid_count
        
        # Save to file
        self.save_data(storage_data)
        
        logger.info(f"Data collection complete: {valid_count} valid, {invalid_count} invalid")
        
        return {
            "status": "success",
            "total_funds": len(results),
            "valid_funds": valid_count,
            "invalid_funds": invalid_count,
            "storage_path": self.funds_file
        }
    
    def save_data(self, data):
        """Save data to JSON file - handles both dict and list formats"""
        # Normalize to dict format
        if isinstance(data, list):
            # Convert list to dict format
            normalized_data = {
                "metadata": {
                    "scraped_at": datetime.now().isoformat(),
                    "total_funds": len(data),
                    "source": "groww.in",
                    "amc": "Parag Parikh AMC"
                },
                "funds": {}
            }
            valid_count = 0
            invalid_count = 0
            
            for fund in data:
                fund_name = fund.get("fund_name", "Unknown")
                if fund.get("validation_status") == "valid":
                    normalized_data["funds"][fund_name] = fund
                    valid_count += 1
                else:
                    invalid_count += 1
            
            normalized_data["metadata"]["valid_funds"] = valid_count
            normalized_data["metadata"]["invalid_funds"] = invalid_count
            data = normalized_data
        elif isinstance(data, dict) and "funds" not in data:
            # If it's a dict but missing "funds" key, wrap it
            data = {"funds": data, "metadata": data.get("metadata", {})}
        
        with open(self.funds_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Data saved to {self.funds_file}")
    
    def load_data(self) -> Optional[Dict]:
        """Load data from storage - normalizes to consistent dict format"""
        if not os.path.exists(self.funds_file):
            logger.warning(f"Storage file not found: {self.funds_file}")
            return None
        
        try:
            with open(self.funds_file, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            # Normalize to dict format with "funds" key
            if isinstance(raw_data, list):
                # Convert list to dict format
                data = {
                    "metadata": {
                        "scraped_at": datetime.now().isoformat(),
                        "total_funds": len(raw_data),
                        "source": "groww.in",
                        "amc": "Parag Parikh AMC"
                    },
                    "funds": {}
                }
                valid_count = 0
                invalid_count = 0
                
                for fund in raw_data:
                    fund_name = fund.get("fund_name", "Unknown")
                    if fund.get("validation_status") == "valid":
                        data["funds"][fund_name] = fund
                        valid_count += 1
                    else:
                        invalid_count += 1
                
                data["metadata"]["valid_funds"] = valid_count
                data["metadata"]["invalid_funds"] = invalid_count
                
                # Save normalized format back
                self.save_data(data)
            elif isinstance(raw_data, dict):
                if "funds" not in raw_data:
                    # Old format - convert
                    data = {"funds": raw_data, "metadata": raw_data.get("metadata", {})}
                    self.save_data(data)
                else:
                    data = raw_data
            else:
                logger.error(f"Unexpected data format: {type(raw_data)}")
                return None
            
            logger.info(f"Data loaded from {self.funds_file}")
            return data
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return None
    
    def get_fund_by_name(self, fund_name: str) -> Optional[Dict]:
        """Get fund data by name (fuzzy matching)"""
        data = self.load_data()
        if not data:
            return None
        
        funds = data.get("funds", {})
        
        # Normalize fund names for comparison
        def normalize_name(name):
            # Remove extra spaces, convert to lowercase
            return ' '.join(name.lower().split())
        
        fund_name_normalized = normalize_name(fund_name)
        
        # Exact match first
        if fund_name in funds:
            return funds[fund_name]
        
        # Normalized exact match
        for stored_name, fund_data in funds.items():
            if normalize_name(stored_name) == fund_name_normalized:
                return fund_data
        
        # Fuzzy match - extract key words (fund type)
        # Extract words between "Parag Parikh" and "Direct Growth"
        def extract_fund_type(name):
            name_lower = name.lower()
            # Pattern: "parag parikh" ... "direct growth"
            if 'parag parikh' in name_lower and 'direct growth' in name_lower:
                start = name_lower.find('parag parikh') + len('parag parikh')
                end = name_lower.find('direct growth')
                fund_type = name_lower[start:end].strip()
                # Remove "fund" if present
                fund_type = fund_type.replace('fund', '').strip()
                return fund_type
            return None
        
        query_fund_type = extract_fund_type(fund_name)
        
        if query_fund_type:
            for stored_name, fund_data in funds.items():
                stored_fund_type = extract_fund_type(stored_name)
                if stored_fund_type and query_fund_type in stored_fund_type or stored_fund_type in query_fund_type:
                    return fund_data
        
        # Last resort: partial match
        fund_name_lower = fund_name.lower()
        for stored_name, fund_data in funds.items():
            stored_lower = stored_name.lower()
            # Check if key words match
            query_words = set(fund_name_lower.split())
            stored_words = set(stored_lower.split())
            # If most key words match
            common_words = query_words.intersection(stored_words)
            if len(common_words) >= 3:  # At least 3 common words
                return fund_data
        
        return None
    
    def get_all_funds(self) -> List[Dict]:
        """Get all stored funds"""
        data = self.load_data()
        if not data:
            return []
        
        return list(data.get("funds", {}).values())
    
    def get_field_value(self, fund_name: str, field: str) -> Optional[Dict]:
        """
        Get a specific field value for a fund.
        Returns dict with value and source_url.
        """
        fund_data = self.get_fund_by_name(fund_name)
        if not fund_data:
            return None
        
        field_value = fund_data.get(field)
        if field_value is None:
            return None
        
        return {
            "fund_name": fund_data.get("fund_name"),
            "field": field,
            "value": field_value,
            "source_url": fund_data.get("source_url")
        }


def main():
    """Main function to scrape and store all funds"""
    print("="*70)
    print("DATA COLLECTION AND STORAGE")
    print("="*70)
    print("\nScraping all Parag Parikh funds from Groww...\n")
    
    storage = DataStorage()
    result = storage.scrape_and_store_all_funds()
    
    print("\n" + "="*70)
    print("STORAGE SUMMARY")
    print("="*70)
    print(f"Total funds processed: {result['total_funds']}")
    print(f"Valid funds stored: {result['valid_funds']}")
    print(f"Invalid funds: {result['invalid_funds']}")
    print(f"Storage location: {result['storage_path']}")
    print("="*70 + "\n")
    
    # Display stored funds
    funds = storage.get_all_funds()
    if funds:
        print(f"\nStored {len(funds)} funds:")
        for fund in funds:
            print(f"  - {fund['fund_name']}")
        print()


if __name__ == "__main__":
    main()

