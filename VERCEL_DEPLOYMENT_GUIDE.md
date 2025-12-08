# Complete Vercel Deployment Guide

This guide will walk you through deploying your RAG-based Mutual Fund FAQ Assistant on Vercel from scratch.

## Prerequisites

1. **GitHub Account** - Your code must be in a GitHub repository
2. **Vercel Account** - Sign up at [vercel.com](https://vercel.com) (free tier is sufficient)
3. **Google Gemini API Key** - Get one from [Google AI Studio](https://aistudio.google.com/app/apikey)

---

## Step 1: Verify Your Repository

Make sure your code is pushed to GitHub:

```bash
git status  # Should show "working tree clean"
git push origin main  # Push any pending changes
```

**Why:** Vercel pulls code directly from GitHub, so all your code must be there.

---

## Step 2: Create a New Project on Vercel

1. **Go to Vercel Dashboard**
   - Visit [vercel.com](https://vercel.com)
   - Sign in or create an account
   - Click **"Add New..."** → **"Project"**

2. **Import Your Repository**
   - Click **"Import Git Repository"**
   - Select your GitHub account
   - Find and select **"Milestone1"** repository
   - Click **"Import"**

**Why:** This connects Vercel to your GitHub repo so it can deploy automatically.

---

## Step 3: Configure Project Settings

### 3.1 Framework Preset
- **Framework Preset:** Select **"Other"** or **"Vite"** (Vercel will auto-detect)
- **Root Directory:** Leave **empty** (project root is correct)

**Why:** Your project uses a custom setup with both Python API and React frontend, so we use "Other" and let `vercel.json` handle the configuration.

### 3.2 Build Settings
- **Build Command:** Leave **empty** (handled by `vercel.json`)
- **Output Directory:** Leave **empty** (handled by `vercel.json`)
- **Install Command:** Leave **empty** (Vercel auto-detects)

**Why:** The `vercel.json` file already specifies how to build both the frontend and API, so we don't need to set these manually.

### 3.3 Environment Variables
Click **"Environment Variables"** and add:

| Name | Value | Environment |
|------|-------|-------------|
| `GOOGLE_API_KEY` | Your Google Gemini API key | Production, Preview, Development |
| `VECTOR_DB_PATH` | `/tmp/vector_db` | Production, Preview, Development |

**How to get Google API Key:**
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the key and paste it in Vercel

**Why:**
- `GOOGLE_API_KEY`: Required for Gemini API to generate embeddings and answers
- `VECTOR_DB_PATH`: Set to `/tmp` because Vercel serverless functions use `/tmp` for temporary storage (read-only filesystem except `/tmp`)

---

## Step 4: Deploy

1. **Click "Deploy"**
   - Vercel will start building your project
   - This may take 3-5 minutes on first deployment

2. **Watch the Build Logs**
   - You'll see build progress in real-time
   - Look for any errors (they'll be highlighted in red)

**What happens during build:**
- **Frontend Build:** Vercel runs `npm install` and `npm run build` in the `frontend/` directory
- **API Setup:** Vercel detects Python files in `api/` and sets up serverless functions
- **File Copying:** The API functions copy data files to `/tmp` for runtime access

---

## Step 5: Verify Deployment

### 5.1 Check Build Status
- If build succeeds, you'll see **"Ready"** status
- Click on your deployment to see the URL (e.g., `milestone1-xyz.vercel.app`)

### 5.2 Test the Application

1. **Visit Your Deployment URL**
   - You should see the React frontend

2. **Check Backend Connection**
   - The frontend will automatically check `/api/health`
   - You should see "Backend connected" status

3. **Test a Query**
   - Try: "What is the expense ratio for ELSS fund?"
   - The system should respond with data and a source link

### 5.3 Common Issues & Solutions

**Issue: 404 Error on Root URL**
- **Solution:** Check that `vercel.json` routes are correct (already configured)

**Issue: "Backend not connected"**
- **Check:** Go to `https://your-app.vercel.app/api/health`
- **Should return:** `{"status":"healthy","service":"Mutual Fund FAQ Assistant (RAG)"}`
- **If error:** Check build logs for Python function errors

**Issue: "API Key not found"**
- **Solution:** Verify `GOOGLE_API_KEY` is set in Vercel environment variables
- **Note:** After adding env vars, you need to **redeploy** (Vercel will prompt you)

**Issue: "RAG pipeline not initialized"**
- **Solution:** The first query will initialize it (may take 10-20 seconds)
- **Check:** Look at function logs in Vercel dashboard

---

## Step 6: Understanding the Deployment Structure

### How It Works:

```
Your Vercel Deployment:
├── /api/* → Python serverless functions (api/query.py, api/health.py, etc.)
├── / → React frontend (frontend/dist/index.html)
└── Static assets (JS, CSS) → frontend/dist/assets/*
```

### File Flow:

1. **User visits** `your-app.vercel.app`
2. **Vercel routes** to `frontend/dist/index.html` (React app)
3. **Frontend makes API calls** to `/api/query` or `/api/health`
4. **Vercel routes** `/api/*` to Python functions in `api/` folder
5. **Python functions** load data from `/tmp/vector_db/` (copied during initialization)

---

## Step 7: Monitor and Debug

### View Logs:
1. Go to Vercel Dashboard → Your Project
2. Click **"Deployments"** tab
3. Click on a deployment
4. Click **"Functions"** tab to see serverless function logs
5. Click on a function (e.g., `api/query`) to see real-time logs

### Debug Tips:
- **Function Timeout:** Vercel free tier has 10s timeout for Hobby plan
- **Cold Starts:** First request after inactivity may take 5-10 seconds
- **Memory:** Each function has 1024MB RAM limit on free tier
- **Size Limit:** Functions must be under 250MB unzipped

---

## Step 8: Automatic Deployments

Vercel automatically deploys when you:
- **Push to main branch** → Production deployment
- **Create a pull request** → Preview deployment
- **Push to other branches** → Preview deployment

**To trigger manual redeploy:**
1. Go to Vercel Dashboard → Your Project
2. Click **"Deployments"**
3. Click **"..."** on any deployment
4. Click **"Redeploy"**

---

## Project Configuration Files Explained

### `vercel.json`
- **Purpose:** Tells Vercel how to build and route your app
- **Builds:** 
  - Python API functions from `api/**/*.py`
  - React frontend from `frontend/package.json`
- **Routes:**
  - `/api/*` → Python serverless functions
  - `/*` → React frontend (SPA routing)

### `requirements.txt`
- **Purpose:** Python dependencies for serverless functions
- **Optimized:** Removed heavy packages (ChromaDB, pandas, etc.) to stay under size limits

### `frontend/package.json`
- **Purpose:** React frontend dependencies
- **Build:** Runs `vite build` to create `frontend/dist/`

---

## Environment Variables Reference

| Variable | Required | Purpose | Example |
|----------|----------|---------|---------|
| `GOOGLE_API_KEY` | ✅ Yes | Gemini API for embeddings & LLM | `AIza...` |
| `VECTOR_DB_PATH` | ⚠️ Optional | Vector DB location (auto-set to `/tmp` in production) | `/tmp/vector_db` |

---

## Troubleshooting Checklist

- [ ] Code is pushed to GitHub
- [ ] Vercel project is connected to GitHub repo
- [ ] `GOOGLE_API_KEY` is set in Vercel environment variables
- [ ] Build completes without errors
- [ ] `/api/health` endpoint returns success
- [ ] Frontend loads without 404 errors
- [ ] Test query returns a response

---

## Next Steps After Deployment

1. **Custom Domain** (Optional):
   - Go to Project Settings → Domains
   - Add your custom domain

2. **Monitor Usage**:
   - Check Vercel dashboard for function invocations
   - Monitor API usage in Google Cloud Console

3. **Optimize Performance**:
   - First query may be slow (cold start + data initialization)
   - Subsequent queries should be faster (warm functions)

---

## Support

If you encounter issues:
1. Check Vercel build logs
2. Check function logs in Vercel dashboard
3. Test `/api/health` endpoint directly
4. Verify environment variables are set correctly

Good luck with your deployment! 🚀

