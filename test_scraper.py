"""
Test script to verify scraper on a single URL
"""

from scraper import GrowwMFScraper
import json

def test_single_fund():
    """Test scraper on a single fund URL"""
    scraper = GrowwMFScraper()
    
    # Test with the ELSS fund (has all fields including lock-in)
    test_url = "https://groww.in/mutual-funds/parag-parikh-elss-tax-saver-fund-direct-growth"
    fund_name = "Parag Parikh ELSS Tax Saver Fund Direct Growth"
    
    print(f"Testing scraper on: {fund_name}")
    print(f"URL: {test_url}\n")
    
    result = scraper.scrape_fund(fund_name, test_url, save_html=True)
    
    print("\n" + "="*60)
    print("EXTRACTED DATA:")
    print("="*60)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("="*60)
    
    # Check against expected values
    expected = {
        "expense_ratio": "0.62%",
        "exit_load": "Nil",
        "minimum_sip": "₹1000",
        "lock_in": "3Y",
        "riskometer": "Moderately High Risk",
        "benchmark": "Nifty 500 Total Return Index"
    }
    
    print("\n" + "="*60)
    print("VALIDATION CHECK:")
    print("="*60)
    for field, expected_value in expected.items():
        actual_value = result.get(field)
        if actual_value:
            # Normalize for comparison
            actual_normalized = str(actual_value).strip()
            expected_normalized = str(expected_value).strip()
            
            # Flexible comparison (case-insensitive, whitespace)
            if actual_normalized.lower() == expected_normalized.lower():
                print(f"✓ {field}: {actual_value} (matches expected)")
            else:
                print(f"⚠ {field}: {actual_value} (expected: {expected_value})")
        else:
            print(f"✗ {field}: NOT FOUND")
    
    print("="*60)
    
    return result

if __name__ == "__main__":
    test_single_fund()

