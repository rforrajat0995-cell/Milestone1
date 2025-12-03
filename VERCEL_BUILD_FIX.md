# Fix for Vercel Build Error: "No Output Directory named 'dist' found"

## Problem

Vercel couldn't find the `dist` directory after the build completed.

## Solution

The issue is with how Vercel's `@vercel/static-build` works. When you specify:
- **Build Command**: `cd frontend && npm install && npm run build`
- **Output Directory**: `frontend/dist`

Vercel runs the build command from the root, but the output directory needs to be relative to where the build actually runs.

## Fixed Configuration

### Option 1: Use vercel.json (Recommended)

The `vercel.json` is already updated with:
```json
{
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "dist"
      }
    }
  ]
}
```

### Option 2: Vercel Dashboard Settings

In Vercel dashboard, set:

**Build Command**: `cd frontend && npm install && npm run build`

**Output Directory**: `frontend/dist`

**OR** (if that doesn't work):

**Build Command**: `cd frontend && npm install && npm run build`

**Output Directory**: `dist`

**Root Directory**: `frontend`

## Why This Happens

1. When you run `cd frontend && npm run build`, Vite creates `frontend/dist/`
2. But `@vercel/static-build` runs the build command and looks for output relative to the build context
3. The `distDir` in the config should match where the build actually outputs

## Verification

After fixing, the build should:
1. ✅ Install dependencies
2. ✅ Build frontend
3. ✅ Find `frontend/dist/` directory
4. ✅ Deploy successfully

## If Still Not Working

Try this alternative approach:

1. **Root Directory**: Set to `frontend` in Vercel dashboard
2. **Build Command**: `npm install && npm run build`
3. **Output Directory**: `dist`

This makes Vercel treat `frontend/` as the root, so `dist` is directly accessible.

