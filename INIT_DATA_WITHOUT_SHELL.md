# Initialize Data Without Shell Access (Free Tier)

Since Render Shell requires payment, here are alternatives to initialize your data:

## Option 1: Add Initialization Endpoint (Recommended)

Create an endpoint that initializes data when called. Add this to `backend_rag_api.py`:

```python
@app.route('/init', methods=['POST'])
def initialize_data():
    """Initialize data - call this once after deployment"""
    import subprocess
    import sys
    
    try:
        # Run scraper
        result1 = subprocess.run([sys.executable, 'main.py'], 
                                capture_output=True, text=True, timeout=300)
        
        # Run index builder
        result2 = subprocess.run([sys.executable, 'build_rag_index.py'], 
                                capture_output=True, text=True, timeout=300)
        
        return jsonify({
            "success": True,
            "message": "Data initialized successfully",
            "scraper_output": result1.stdout[-500:],  # Last 500 chars
            "index_output": result2.stdout[-500:]
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
```

Then call it:
```bash
curl -X POST https://your-service-url.onrender.com/init
```

## Option 2: Use Render's Manual Deploy with Script

1. Create `init_and_start.sh`:
```bash
#!/bin/bash
if [ ! -f "data/storage/funds_database.json" ]; then
    echo "Initializing data..."
    python main.py
    python build_rag_index.py
fi
gunicorn wsgi:application --bind 0.0.0.0:$PORT --timeout 120 --log-level info
```

2. Update Procfile:
```
web: bash init_and_start.sh
```

3. Push to GitHub - Render will auto-deploy and initialize on first run

## Option 3: Pre-build Data Locally and Commit

1. Run locally:
```bash
python main.py
python build_rag_index.py
```

2. Commit the data files:
```bash
git add data/storage/funds_database.json
git commit -m "Add pre-initialized data"
git push
```

3. Render will use the committed data

**Note**: This works but increases repo size. Better to use Option 1 or 2.

## Option 4: Use GitHub Actions (Advanced)

Create `.github/workflows/init-data.yml` to initialize data on deploy.

## Recommended: Option 1

Add the `/init` endpoint - it's the cleanest solution for free tier.

