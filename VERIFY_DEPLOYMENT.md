# How to Verify Deployment Without Shell Access

## Method 1: Check Service Status in Render Dashboard

1. **Go to Render Dashboard** → Your Service
2. **Look at the top of the page** - you should see:
   - **Status**: "Live" (green indicator)
   - **Service URL**: `https://your-service-name.onrender.com`
   - Copy this URL

## Method 2: Test Health Endpoint

### Option A: Using Browser

1. **Get your service URL** from Render dashboard (top of service page)
2. **Add `/health` to the end**:
   ```
   https://your-service-name.onrender.com/health
   ```
3. **Open in browser** - you should see JSON response

### Option B: Using curl (Terminal)

```bash
curl https://your-service-name.onrender.com/health
```

### Option C: Using Postman or Browser DevTools

1. Open browser DevTools (F12)
2. Go to Console tab
3. Run:
   ```javascript
   fetch('https://your-service-name.onrender.com/health')
     .then(r => r.json())
     .then(console.log)
   ```

## Method 3: Check Logs for Success Indicators

In Render Dashboard → Your Service → **Logs** tab, look for:

**✅ Good Signs:**
- "Starting WSGI application..."
- "Successfully imported backend_rag_api.app"
- "Starting gunicorn" or "Booting worker"
- "Listening at: http://0.0.0.0:XXXX"
- No "Port scan timeout" errors

**❌ Bad Signs:**
- "Port scan timeout"
- "No open ports detected"
- Python traceback errors
- Import errors

## Method 4: Test Query Endpoint

Try the query endpoint:

```bash
curl -X POST https://your-service-name.onrender.com/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'
```

Or in browser console:
```javascript
fetch('https://your-service-name.onrender.com/query', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({query: 'test'})
})
.then(r => r.json())
.then(console.log)
```

## Method 5: Check Service Metrics

In Render Dashboard → Your Service → **Metrics** tab:
- Should show CPU/Memory usage if service is running
- If all zeros, service might not be running

## Common Issues:

### Issue: "This site can't be reached" or "Connection refused"
**Possible causes:**
- Service is still deploying (wait 5-10 minutes)
- Service spun down (free tier - first request takes 30-60 seconds)
- Wrong URL

**Solution:**
- Wait 30-60 seconds and try again (free tier spin-up)
- Verify URL in Render dashboard
- Check service status is "Live"

### Issue: "404 Not Found"
**Possible causes:**
- Wrong endpoint
- Service running but route doesn't exist

**Solution:**
- Try `/health` endpoint specifically
- Check logs for route registration

### Issue: "500 Internal Server Error"
**Possible causes:**
- App is running but has errors
- RAG pipeline not initialized (expected - need to initialize data)

**Solution:**
- Check logs for specific error
- This might be normal if data isn't initialized yet

## Finding Your Service URL:

1. Go to Render Dashboard
2. Click on your service name
3. Look at the **top of the page** - there should be a URL like:
   - `https://mutual-fund-faq-backend-XXXX.onrender.com`
   - Or similar

4. **Copy that exact URL** and use it for testing

## Quick Verification Checklist:

- [ ] Service status shows "Live" (green)
- [ ] Service URL is visible in dashboard
- [ ] `/health` endpoint returns JSON (even if error)
- [ ] Logs show "Starting gunicorn" or "Booting worker"
- [ ] No "port scan timeout" in recent logs
- [ ] Service responds (even if slowly on free tier)

