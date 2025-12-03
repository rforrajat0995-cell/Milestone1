# Vercel Dashboard Settings (If vercel.json doesn't work)

If you're still getting the "No Output Directory" error, try these settings in the Vercel dashboard:

## Option 1: Standard Settings (Recommended)

Go to **Project Settings** → **General** → **Build & Development Settings**

| Field | Value |
|-------|-------|
| **Framework Preset** | Other |
| **Root Directory** | (leave empty) |
| **Build Command** | `cd frontend && npm install && npm run build` |
| **Output Directory** | `frontend/dist` |
| **Install Command** | `npm install` (default) |

## Option 2: Alternative (If Option 1 doesn't work)

| Field | Value |
|-------|-------|
| **Framework Preset** | Vite |
| **Root Directory** | `frontend` |
| **Build Command** | `npm install && npm run build` |
| **Output Directory** | `dist` |
| **Install Command** | `npm install` |

**Note**: If using Option 2, you'll need to update `vercel.json` routes or remove it temporarily.

## Option 3: Manual Override

If both don't work, try:

1. **Delete** the `vercel.json` file temporarily
2. Set in dashboard:
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Output Directory**: `dist`
3. Deploy
4. If it works, we can update `vercel.json` accordingly

## Environment Variables (Still Required)

Don't forget:
- **GOOGLE_API_KEY**: Your actual API key

## After Fixing

Once deployment succeeds:
1. Test: `https://your-app.vercel.app/api/health`
2. Test: `https://your-app.vercel.app` (frontend)

