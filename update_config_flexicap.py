"""
Script to help update Flexi Cap Fund configuration
If the fund doesn't exist on Groww, we can either:
1. Remove it from config
2. Update with correct URL if known
3. Keep it but handle gracefully in the system
"""

import requests
import config

def check_flexi_cap_urls():
    """Check various possible URLs for Flexi Cap Fund"""
    base = "https://groww.in/mutual-funds/"
    
    possible_urls = [
        "parag-parikh-flexi-cap-fund-direct-growth",
        "parag-parikh-flexicap-fund-direct-growth",
        "parag-parikh-flexi-cap-fund",
        "parag-parikh-flexi-cap-direct-growth",
        "parag-parikh-flexi-cap",
    ]
    
    print("Checking possible Flexi Cap Fund URLs:")
    print("="*80)
    
    found = False
    for url_slug in possible_urls:
        url = base + url_slug
        try:
            response = requests.get(
                url, 
                timeout=5, 
                headers={'User-Agent': config.USER_AGENT},
                allow_redirects=True
            )
            if response.status_code == 200:
                print(f"✅ FOUND: {url}")
                found = True
                # Check if it's actually the Flexi Cap fund page
                if "flexi" in response.text.lower() or "flexicap" in response.text.lower():
                    print(f"   ✓ Page contains 'flexi' - likely correct!")
                break
            else:
                print(f"❌ {url_slug}: {response.status_code}")
        except Exception as e:
            print(f"❌ {url_slug}: Error - {str(e)[:50]}")
    
    if not found:
        print("\n" + "="*80)
        print("⚠️  Flexi Cap Fund not found on Groww")
        print("\nOptions:")
        print("1. Remove from config if fund doesn't exist")
        print("2. Update URL in config.py if you know the correct one")
        print("3. The system will handle it gracefully (show 'not available' message)")

if __name__ == "__main__":
    check_flexi_cap_urls()

