"""
Configuration file for Groww mutual fund scraper
Contains fund names and their corresponding URL slugs
"""

BASE_URL = "https://groww.in/mutual-funds/"

# Parag Parikh AMC funds mapping: fund_name -> URL slug
# URLs verified and updated as per user requirements
PARAG_PARIKH_FUNDS = {
    "Parag Parikh Flexi Cap Fund Direct Growth": "parag-parikh-long-term-value-fund-direct-growth",
    "Parag Parikh ELSS Tax Saver Fund Direct Growth": "parag-parikh-elss-tax-saver-fund-direct-growth",
    "Parag Parikh Conservative Hybrid Fund Direct Growth": "parag-parikh-conservative-hybrid-fund-direct-growth",
    "Parag Parikh Liquid Fund Direct Growth": "parag-parikh-liquid-fund-direct-growth",
    "Parag Parikh Arbitrage Fund Direct Growth": "parag-parikh-arbitrage-fund-direct-growth",
    "Parag Parikh Dynamic Asset Allocation Fund Direct Growth": "parag-parikh-dynamic-asset-allocation-fund-direct-growth",
    "Parag Parikh Long Term Value Fund Direct Growth": "parag-parikh-long-term-value-fund-direct-growth",
}

# Request settings
REQUEST_TIMEOUT = 30
REQUEST_DELAY = 2  # seconds between requests to avoid rate limiting
MAX_RETRIES = 3

# User agent to mimic browser requests
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

