# Fixing 404 Error on Vercel

## The Problem
You're getting a 404 error after deployment, which means Vercel can't find your frontend files.

## Root Cause
When using `@vercel/static-build` with a nested `frontend/` folder, Vercel needs to know:
1. Where to find the build output
2. How to route requests to those files

## Solution Options

### Option 1: Check Vercel Project Settings (Recommended First Step)

1. Go to your Vercel project dashboard
2. Click **Settings** → **General**
3. Check these settings:
   - **Root Directory:** Should be **empty** (or set to project root)
   - **Build Command:** Should be **empty** (let vercel.json handle it)
   - **Output Directory:** Should be **empty** (let vercel.json handle it)
   - **Install Command:** Should be **empty** (auto-detected)

4. If any of these are set incorrectly, clear them and redeploy.

### Option 2: Use Vercel Project Settings Instead of vercel.json

If `vercel.json` isn't working, try configuring in Vercel dashboard:

1. Go to **Settings** → **General**
2. Set:
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
   - **Install Command:** `npm install`

3. Then update `vercel.json` to only handle API routes:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/**/*.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/$1"
    }
  ]
}
```

**Note:** This approach requires setting Root Directory to `frontend` in Vercel dashboard.

### Option 3: Move Frontend to Root (Alternative)

If the above doesn't work, you could restructure:

1. Move `frontend/*` files to project root
2. Update `vercel.json` accordingly
3. This is more work but guarantees it will work

## Current Configuration

Your current `vercel.json` should work IF:
- Vercel project settings are correct (all empty/default)
- The build completes successfully
- Files are output to `frontend/dist/`

## Debugging Steps

1. **Check Build Logs:**
   - Go to Vercel → Your Project → Deployments
   - Click on the latest deployment
   - Check if frontend build succeeded
   - Look for where files are being output

2. **Check Function Logs:**
   - Go to Functions tab
   - See if there are any errors

3. **Test Direct File Access:**
   - Try: `https://your-app.vercel.app/index.html`
   - Try: `https://your-app.vercel.app/api/health`
   - This tells you if files exist but routing is wrong

4. **Check File Structure:**
   - In build logs, look for "Output Directory" or where files are placed
   - Verify the path matches your routes in `vercel.json`

## Quick Fix to Try

1. **Clear all Vercel project settings** (Root Directory, Build Command, Output Directory)
2. **Use the current `vercel.json`** (already committed)
3. **Redeploy**
4. If still 404, try **Option 2** above (set Root Directory to `frontend` in dashboard)

## Expected Behavior

After successful deployment:
- `https://your-app.vercel.app/` → Should show React app
- `https://your-app.vercel.app/api/health` → Should return JSON
- `https://your-app.vercel.app/api/query` → Should handle queries

If you're still getting 404, the issue is likely in Vercel project settings, not the code.

