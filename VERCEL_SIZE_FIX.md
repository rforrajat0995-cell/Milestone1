# Vercel Serverless Function Size Fix

## Problem
Serverless function exceeded 250 MB unzipped size limit.

## Root Cause
Heavy dependencies that aren't needed at runtime in API functions:
- `pandas` (~50-100 MB)
- `beautifulsoup4` + `lxml` (~20-30 MB) - only needed for scraping
- `flask` + `flask-cors` (~10-20 MB) - not needed in serverless functions
- `requests` (~5-10 MB) - not used in API functions

## Solution Applied

### 1. Optimized `requirements.txt`
Removed unnecessary dependencies, keeping only:
- `google-generativeai` - for embeddings and LLM
- `chromadb` - for vector database
- `python-dotenv` - for environment variables

### 2. Made Scraper Optional
Updated `data_storage.py` to make scraper imports optional:
- Scraper is only needed for data collection (local)
- Not needed in API functions (Vercel)

### 3. Size Reduction
**Before**: ~250+ MB (with all dependencies)
**After**: ~150-200 MB (only essential dependencies)

## For Local Development

If you need to run scraping locally, install additional dependencies:

```bash
pip install requests beautifulsoup4 lxml pandas flask flask-cors
```

Or use the full requirements file (if you create one for local dev).

## Verification

The optimized requirements should now:
- ✅ Build successfully on Vercel
- ✅ Stay under 250 MB limit
- ✅ Work for API functions (query, health, funds)
- ⚠️ Scraping won't work (but that's fine - data is pre-built)

## Next Steps

1. Redeploy on Vercel
2. Should build successfully now
3. Test API endpoints

