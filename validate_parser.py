"""
Validation script to test parser on specific fund
"""

from scraper import GrowwMFScraper
import json

def validate_arbitrage_fund():
    """Validate parser on Parag Parikh Arbitrage Fund"""
    scraper = GrowwMFScraper()
    
    # Parag Parikh Arbitrage Fund
    fund_name = "Parag Parikh Arbitrage Fund Direct Growth"
    test_url = "https://groww.in/mutual-funds/parag-parikh-arbitrage-fund-direct-growth"
    
    print("="*70)
    print("VALIDATING PARSER FOR PARAG PARIKH ARBITRAGE FUND")
    print("="*70)
    print(f"\nFund: {fund_name}")
    print(f"URL: {test_url}\n")
    
    # Scrape the fund
    result = scraper.scrape_fund(fund_name, test_url)
    
    # Display results
    print("\n" + "="*70)
    print("EXTRACTED DATA:")
    print("="*70)
    
    if "error" in result:
        print(f"❌ ERROR: {result['error']}")
        return
    
    print(f"✓ Source URL: {result.get('source_url', 'N/A')}")
    print(f"✓ Riskometer (Risk Factor): {result.get('riskometer', 'NOT FOUND')}")
    print(f"✓ Expense Ratio: {result.get('expense_ratio', 'NOT FOUND')}")
    print(f"✓ Exit Load: {result.get('exit_load', 'N/A')}")
    print(f"✓ Minimum SIP: {result.get('minimum_sip', 'N/A')}")
    print(f"✓ Lock-in: {result.get('lock_in', 'N/A')}")
    print(f"✓ Benchmark: {result.get('benchmark', 'N/A')}")
    
    print("\n" + "-"*70)
    print("VALIDATION STATUS:")
    print("-"*70)
    
    if result.get('validation_status') == 'valid':
        print("✅ ALL FIELDS VALIDATED SUCCESSFULLY")
    else:
        print("⚠️  VALIDATION ISSUES FOUND:")
        for error in result.get('validation_errors', []):
            print(f"   - {error}")
    
    # Answer the specific question
    print("\n" + "="*70)
    print("ANSWER TO YOUR QUESTION:")
    print("="*70)
    print(f"\nRisk Factor (Riskometer): {result.get('riskometer', 'NOT FOUND')}")
    print(f"Expense Ratio: {result.get('expense_ratio', 'NOT FOUND')}")
    print(f"Source URL: {result.get('source_url', 'NOT FOUND')}")
    print("="*70 + "\n")
    
    return result

if __name__ == "__main__":
    validate_arbitrage_fund()

