# Troubleshooting 404 Error on Vercel

## What URL Are You Visiting?

The 404 error depends on which URL you're trying to access:

### If visiting root URL (`/`)
Try these in order:
1. `https://your-app.vercel.app/` - Should serve frontend
2. `https://your-app.vercel.app/index.html` - Direct HTML file
3. `https://your-app.vercel.app/api/health` - Test API

### If visiting API endpoint
Try:
- `https://your-app.vercel.app/api/health`
- `https://your-app.vercel.app/api/query`
- `https://your-app.vercel.app/api/funds`

## Common Issues

### Issue 1: Frontend Not Built
**Symptom:** 404 on root URL

**Check:**
1. Go to Vercel Dashboard → Your Deployment → Build Logs
2. Look for "Building frontend" step
3. Verify it completed successfully

**Fix:**
- Ensure Build Command is: `cd frontend && npm install && npm run build`
- Ensure Output Directory is: `frontend/dist`

### Issue 2: Route Mismatch
**Symptom:** 404 on all URLs

**Check:**
- `vercel.json` routes configuration
- Build output location vs route destination

**Current Fix Applied:**
- Route: `dest: "/frontend/dist/$1"` (matches build output)

### Issue 3: API Functions Not Found
**Symptom:** 404 on `/api/*` endpoints

**Check:**
1. Files exist in `api/` directory
2. Files are named correctly (`query.py`, `health.py`, `funds.py`)
3. Functions export `handler` class

## Quick Test Commands

Test from terminal:
```bash
# Test health endpoint
curl https://your-app.vercel.app/api/health

# Test frontend
curl https://your-app.vercel.app/
```

## Next Steps

1. **Redeploy** after the route fix
2. **Wait for build to complete**
3. **Test the URLs above**
4. **Check Vercel logs** if still 404

## If Still Not Working

1. Check Vercel deployment logs for errors
2. Verify all files are in Git
3. Try accessing `/index.html` directly
4. Check that `frontend/dist/index.html` exists after build

