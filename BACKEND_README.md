# Backend Architecture - Groww MF FAQ Assistant

## Overview

This backend system follows the recommended architecture:
- **Precompute data**: Scrape and store mutual fund data with source URLs
- **Structured storage**: JSON-based storage for fast lookups
- **Query handler**: Natural language query processing
- **Source URL tracking**: Every answer includes the source URL

## Architecture Components

### 1. Data Storage (`data_storage.py`)
- Scrapes all Parag Parikh funds from Groww
- Stores validated data in `data/storage/funds_database.json`
- Provides fuzzy matching for fund name lookups

### 2. Query Handler (`query_handler.py`)
- Parses natural language queries
- Extracts fund name and field of interest
- Returns answers with source URLs

### 3. Backend API (`backend_api.py`)
- Flask-based REST API
- Endpoints for queries and fund information
- Ready for frontend integration

## Usage

### Step 1: Collect and Store Data

```bash
source venv/bin/activate
python data_storage.py
```

This will:
- Scrape all Parag Parikh funds from Groww
- Validate the data
- Store in `data/storage/funds_database.json`

### Step 2: Test Query Handler

```bash
python test_backend.py
```

Or use the query handler directly:

```python
from query_handler import QueryHandler
from data_storage import DataStorage

storage = DataStorage()
handler = QueryHandler(storage)

query = "Tell me the exit load for Parag Parikh Liquid Fund Direct Growth?"
response = handler.answer_query(query)

print(response['answer'])
print(f"Source: {response['source_url']}")
```

### Step 3: Run Backend API (Optional)

```bash
python backend_api.py
```

Then test with:

```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Tell me the exit load for Parag Parikh Liquid Fund Direct Growth?"}'
```

## Example Query

**Query:** "Tell me the exit load for Parag Parikh Liquid Fund Direct Growth?"

**Response:**
```json
{
  "success": true,
  "answer": "The Exit Load for Parag Parikh Liquid Fund Direct Growth is Nil.",
  "fund_name": "Parag Parikh Liquid Fund Direct Growth",
  "field": "exit_load",
  "value": "Nil",
  "source_url": "https://groww.in/mutual-funds/parag-parikh-liquid-fund-direct-growth",
  "query": "Tell me the exit load for Parag Parikh Liquid Fund Direct Growth?"
}
```

## Supported Fields

- `expense_ratio` - Expense Ratio
- `exit_load` - Exit Load
- `minimum_sip` - Minimum SIP
- `lock_in` - Lock-in Period
- `riskometer` - Riskometer (Risk Factor)
- `benchmark` - Benchmark Index

## Query Examples

- "Tell me the exit load for Parag Parikh Liquid Fund Direct Growth?"
- "What is the expense ratio of Parag Parikh ELSS Tax Saver Fund?"
- "Tell me the riskometer for Parag Parikh Arbitrage Fund"
- "What is the minimum SIP for Parag Parikh Flexi Cap Fund?"

## Data Storage Format

Data is stored in `data/storage/funds_database.json`:

```json
{
  "metadata": {
    "scraped_at": "2025-11-18T22:48:25",
    "total_funds": 7,
    "valid_funds": 6,
    "source": "groww.in",
    "amc": "Parag Parikh AMC"
  },
  "funds": {
    "Parag Parikh Liquid Fund Direct Growth": {
      "fund_name": "Parag Parikh Liquid Fund Direct Growth",
      "source_url": "https://groww.in/mutual-funds/...",
      "expense_ratio": "0.3%",
      "exit_load": "Nil",
      "minimum_sip": "₹1000",
      "lock_in": "N/A",
      "riskometer": "Moderate Risk",
      "benchmark": "NIFTY 50 Arbitrage Total Return Index"
    }
  }
}
```

## Key Features

✅ **Precomputed Data**: All data scraped and stored upfront  
✅ **Source URL Tracking**: Every answer includes source URL  
✅ **Fuzzy Matching**: Handles variations in fund names  
✅ **Validation**: All stored data is validated  
✅ **Natural Language Queries**: Understands various query formats  
✅ **No Investment Advice**: Only provides factual information

## Next Steps

1. **Frontend Integration**: Connect the Flask API to a frontend
2. **Vector Database**: Add RAG capabilities for more complex queries
3. **Caching**: Implement caching for faster responses
4. **Scheduled Updates**: Automate data refresh

