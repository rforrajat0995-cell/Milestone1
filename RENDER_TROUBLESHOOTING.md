# Render Deployment Troubleshooting

## Port Binding Error: "No open ports detected"

### Issue
Render can't detect that your app is listening on a port.

### Solutions (Try in order)

#### Solution 1: Update Start Command in Render Dashboard ⭐ (MOST IMPORTANT)

1. Go to Render Dashboard → Your Service → **Settings**
2. Find **"Start Command"**
3. **Delete** the existing command
4. **Add**: `gunicorn backend_rag_api:app --bind 0.0.0.0:$PORT`
5. Click **"Save Changes"**
6. Wait for redeployment (5-10 minutes)

**Why**: Render dashboard settings override Procfile. You must update it manually.

---

#### Solution 2: Verify Gunicorn is Installed

Check that `gunicorn>=21.2.0` is in `requirements.txt`:
```txt
gunicorn>=21.2.0
```

If not, add it and push to GitHub.

---

#### Solution 3: Check Environment Variables

Ensure these are set in Render:
- `PORT` = `5000` (or leave empty - Render sets it automatically)
- `GOOGLE_API_KEY` = your actual API key
- `FLASK_DEBUG` = `False`

---

#### Solution 4: Verify App Can Start

The app should start even if RAG pipeline fails. Check logs for:
- ✅ "Starting gunicorn" or "Booting worker"
- ❌ Any import errors or initialization failures

---

#### Solution 5: Test Locally with Gunicorn

Test if gunicorn works locally:
```bash
pip install gunicorn
gunicorn backend_rag_api:app --bind 0.0.0.0:5000
```

If this works locally, it should work on Render.

---

#### Solution 6: Check Logs for Errors

In Render Dashboard → Logs tab, look for:
- Import errors
- Missing dependencies
- Initialization failures
- Port binding messages

---

## Common Issues

### Issue: "Module not found"
**Fix**: Ensure all dependencies are in `requirements.txt`

### Issue: "RAG pipeline not initialized"
**Fix**: This is OK - app will still start. Initialize data later using Render Shell.

### Issue: "Timeout during initialization"
**Fix**: RAG pipeline initialization is now lazy - it won't block app startup.

---

## Verification Steps

After updating start command:

1. ✅ Status shows "Live" (green)
2. ✅ Logs show "Starting gunicorn" or "Booting worker"
3. ✅ Health endpoint works: `https://your-app.onrender.com/health`
4. ✅ No "port scan timeout" errors

---

## Still Not Working?

1. **Clear Start Command**: Delete it completely, let Render use Procfile
2. **Check Build Logs**: Ensure `gunicorn` is installed during build
3. **Try Different Port Binding**: `gunicorn backend_rag_api:app --bind 0.0.0.0:${PORT:-5000}`
4. **Contact Support**: Render support is helpful - check their docs

---

## Quick Fix Checklist

- [ ] Updated Start Command in Render dashboard to: `gunicorn backend_rag_api:app --bind 0.0.0.0:$PORT`
- [ ] Saved changes in Render
- [ ] Waited for redeployment (5-10 min)
- [ ] Checked logs for gunicorn startup
- [ ] Tested health endpoint
- [ ] Verified no port scan errors

