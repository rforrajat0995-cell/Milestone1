"""
Main script to run the Groww mutual fund scraper
"""

import json
import os
from datetime import datetime
from scraper import GrowwMFScraper
import logging

logger = logging.getLogger(__name__)


def ensure_data_directory():
    """Create data directories if they don't exist"""
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("data/raw", exist_ok=True)


def save_results(data: list, filename: str = None):
    """
    Save scraped data to JSON file.
    
    Args:
        data: List of dictionaries with scraped data
        filename: Optional filename, defaults to timestamped file
    """
    ensure_data_directory()
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/processed/funds_data_{timestamp}.json"
    else:
        filename = f"data/processed/{filename}"
    
    # Add metadata
    output = {
        "scraped_at": datetime.now().isoformat(),
        "total_funds": len(data),
        "valid_funds": sum(1 for item in data if item.get("validation_status") == "valid"),
        "invalid_funds": sum(1 for item in data if item.get("validation_status") == "invalid"),
        "funds": data
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Results saved to {filename}")
    return filename


def print_summary(data: list):
    """Print summary of scraping results"""
    print("\n" + "="*60)
    print("SCRAPING SUMMARY")
    print("="*60)
    
    total = len(data)
    valid = sum(1 for item in data if item.get("validation_status") == "valid")
    invalid = sum(1 for item in data if item.get("validation_status") == "invalid")
    failed = sum(1 for item in data if "error" in item)
    
    print(f"Total funds: {total}")
    print(f"Successfully scraped: {valid}")
    print(f"Validation failed: {invalid}")
    print(f"Failed to fetch: {failed}")
    print("\n" + "-"*60)
    
    # Print details for each fund
    for item in data:
        status = item.get("validation_status", "unknown")
        fund_name = item.get("fund_name", "Unknown")
        url = item.get("source_url", "N/A")
        
        if status == "valid":
            print(f"✓ {fund_name}")
            print(f"  URL: {url}")
            print(f"  Expense Ratio: {item.get('expense_ratio', 'N/A')}")
            print(f"  Exit Load: {item.get('exit_load', 'N/A')}")
            print(f"  Minimum SIP: {item.get('minimum_sip', 'N/A')}")
            print(f"  Lock-in: {item.get('lock_in', 'N/A')}")
            print(f"  Riskometer: {item.get('riskometer', 'N/A')}")
            print(f"  Benchmark: {item.get('benchmark', 'N/A')}")
        elif "error" in item:
            print(f"✗ {fund_name} - ERROR: {item.get('error')}")
        else:
            print(f"⚠ {fund_name} - VALIDATION FAILED")
            errors = item.get("validation_errors", [])
            for error in errors:
                print(f"    - {error}")
        print()
    
    print("="*60 + "\n")


def main():
    """Main execution function"""
    logger.info("Starting Groww mutual fund scraper")
    
    scraper = GrowwMFScraper()
    
    # Scrape all funds
    results = scraper.scrape_all_funds()
    
    # Save results
    filename = save_results(results)
    
    # Print summary
    print_summary(results)
    
    logger.info(f"Scraping completed. Results saved to {filename}")
    
    return results


if __name__ == "__main__":
    main()

