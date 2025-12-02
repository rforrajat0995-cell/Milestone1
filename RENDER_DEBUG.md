# Debug Render Port Binding Issue

Since you've already updated the start command to use gunicorn, let's debug further.

## Check These Things:

### 1. Check Render Logs

In Render Dashboard → Your Service → **Logs** tab, look for:

**What to look for:**
- ✅ "Starting gunicorn" or "Booting worker"
- ✅ "Listening at: http://0.0.0.0:XXXX"
- ❌ Any import errors
- ❌ "ModuleNotFoundError"
- ❌ "Failed to find application object"
- ❌ Any Python traceback errors

**Share the last 20-30 lines of logs** - this will help identify the issue.

---

### 2. Verify Gunicorn is Installed

Check build logs to see if gunicorn installed:
- Go to Render Dashboard → Your Service → **Events** tab
- Look for build step
- Should see: "Collecting gunicorn" or "Installing gunicorn"

---

### 3. Check Environment Variables

Verify these are set:
- `PORT` - Should be set automatically by Render (you can leave it empty or set to 5000)
- `GOOGLE_API_KEY` - Your actual API key
- `FLASK_DEBUG` - `False`

---

### 4. Test Gunicorn Command Format

Try this alternative start command (if current one doesn't work):

```
gunicorn --bind 0.0.0.0:$PORT backend_rag_api:app
```

Or with explicit workers:
```
gunicorn --bind 0.0.0.0:$PORT --workers 2 backend_rag_api:app
```

---

### 5. Check if App Module is Correct

Verify the Flask app is named `app` in `backend_rag_api.py`:
- Should see: `app = Flask(__name__)`
- This is correct ✅

---

### 6. Possible Issues:

**Issue A: Import Error**
- If RAG pipeline imports fail, app might not start
- Check logs for import errors

**Issue B: PORT Variable Not Set**
- Try: `gunicorn backend_rag_api:app --bind 0.0.0.0:${PORT:-5000}`
- This uses 5000 as fallback if PORT not set

**Issue C: Gunicorn Not Found**
- Check if gunicorn is in requirements.txt
- Should see: `gunicorn>=21.2.0`

**Issue D: App Crashes on Startup**
- RAG pipeline initialization might be crashing
- Check logs for Python errors

---

## Quick Fixes to Try:

### Fix 1: Alternative Start Command
```
gunicorn --bind 0.0.0.0:$PORT --timeout 120 backend_rag_api:app
```

### Fix 2: With Error Logging
```
gunicorn --bind 0.0.0.0:$PORT --log-level debug backend_rag_api:app
```

### Fix 3: Explicit Port Fallback
```
gunicorn backend_rag_api:app --bind 0.0.0.0:${PORT:-5000}
```

---

## What to Share:

Please share:
1. **Last 20-30 lines of Render logs** (from Logs tab)
2. **Build logs** (from Events tab - look for gunicorn installation)
3. **Current start command** (screenshot or copy-paste)

This will help identify the exact issue!

