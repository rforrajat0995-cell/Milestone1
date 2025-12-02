"""
Test script for the backend query handler
Tests the specific query: "Tell me the exit load for Parag Parikh Liquid Fund Direct Growth?"
"""

from query_handler import QueryHandler, format_answer
from data_storage import DataStorage

def test_query():
    """Test the backend with the specific query"""
    print("="*70)
    print("BACKEND QUERY HANDLER TEST")
    print("="*70)
    
    # Initialize
    print("\n1. Initializing storage and query handler...")
    storage = DataStorage()
    handler = QueryHandler(storage)
    
    # Check if data exists
    print("\n2. Checking if data exists...")
    data = storage.load_data()
    if not data:
        print("   ⚠️  No data found. Running data collection first...")
        print("\n   Scraping and storing all funds...")
        storage.scrape_and_store_all_funds()
        print("   ✓ Data collection complete\n")
    else:
        print(f"   ✓ Found data with {len(data.get('funds', {}))} funds")
    
    # Test the specific query
    test_query = "Tell me the exit load for Parag Parikh Liquid Fund Direct Growth?"
    
    print("\n3. Processing query:")
    print(f"   Query: {test_query}\n")
    
    # Process query
    response = handler.answer_query(test_query)
    
    # Display result
    print("4. Response:")
    print("-"*70)
    formatted = format_answer(response)
    print(formatted)
    print("-"*70)
    
    # Detailed breakdown
    print("\n5. Response Details:")
    print(f"   Success: {response.get('success')}")
    if response.get('success'):
        print(f"   Fund Name: {response.get('fund_name')}")
        print(f"   Field: {response.get('field')}")
        print(f"   Value: {response.get('value')}")
        print(f"   Source URL: {response.get('source_url')}")
    else:
        print(f"   Error: {response.get('answer')}")
    
    print("\n" + "="*70)
    
    # Test a few more queries
    print("\n6. Testing additional queries:")
    additional_queries = [
        "What is the expense ratio of Parag Parikh ELSS Tax Saver Fund?",
        "Tell me the riskometer for Parag Parikh Flexi Cap Fund",
        "What is the minimum SIP for Parag Parikh Arbitrage Fund?"
    ]
    
    for q in additional_queries:
        print(f"\n   Query: {q}")
        resp = handler.answer_query(q)
        if resp.get('success'):
            print(f"   ✓ Answer: {resp.get('value')}")
            print(f"   Source: {resp.get('source_url')}")
        else:
            print(f"   ✗ {resp.get('answer')}")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    test_query()

