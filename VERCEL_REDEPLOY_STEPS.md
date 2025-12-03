# Steps to Fix Backend Connection Issue

## Step 1: Redeploy on Vercel

1. Go to **Vercel Dashboard**
2. Click on your project
3. Go to **"Deployments"** tab
4. Find the latest deployment
5. Click the **"..."** menu (three dots)
6. Click **"Redeploy"**
7. Wait for build to complete (3-5 minutes)

## Step 2: Test API Directly

After redeploy, test the API endpoints directly in your browser:

1. **Health Check:**
   ```
   https://your-app-name.vercel.app/api/health
   ```
   Should return JSON: `{"status": "healthy", ...}`

2. **If health works**, the API is fine - it's a frontend issue
3. **If health returns 404**, the API routes aren't working

## Step 3: Check Frontend Build

1. In Vercel Dashboard → Your Deployment → **"Build Logs"**
2. Look for:
   - ✅ "Building frontend" step completed
   - ✅ No errors in frontend build
   - ✅ "Deploying" completed successfully

## Step 4: Clear Browser Cache

Sometimes the old frontend code is cached:
1. **Hard refresh**: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
2. Or open in **Incognito/Private window**

## Step 5: Verify Environment

The frontend should detect production automatically. Check browser console:
1. Open browser **Developer Tools** (F12)
2. Go to **Console** tab
3. Look for any errors
4. Check **Network** tab - see if `/api/health` request is being made

## Troubleshooting

### If `/api/health` returns 404:
- API routes aren't configured correctly
- Check `vercel.json` routes
- Verify `api/` directory structure

### If `/api/health` works but frontend shows disconnected:
- Frontend might be using cached old code
- Hard refresh browser
- Check browser console for errors

### If `/api/health` returns error:
- Check Vercel function logs
- Verify `GOOGLE_API_KEY` is set
- Check build logs for Python errors

## Quick Test Commands

Test from terminal:
```bash
# Test health endpoint
curl https://your-app.vercel.app/api/health

# Should return:
# {"status":"healthy","service":"Mutual Fund FAQ Assistant (RAG)",...}
```

