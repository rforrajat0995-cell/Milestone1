# Quick Vercel Deployment Guide

## ✅ Pre-Deployment Checklist

- [x] Removed Render/Railway files
- [x] Created Vercel serverless functions (`api/` directory)
- [x] Updated frontend to use `/api` paths
- [x] Updated `vercel.json` configuration
- [x] Vector DB committed to Git
- [x] Data files ready

## 🚀 Deploy in 3 Steps

### Step 1: Go to Vercel

1. Visit [vercel.com](https://vercel.com)
2. Sign up/Login with GitHub

### Step 2: Import Project

1. Click **"Add New..."** → **"Project"**
2. Select repository: `rforrajat0995-cell/Milestone1`
3. Click **"Import"**

### Step 3: Configure & Deploy

**Build Settings:**
- Framework: Leave as "Other" (or "Vite")
- Root Directory: Leave empty
- Build Command: `cd frontend && npm install && npm run build`
- Output Directory: `frontend/dist`

**Environment Variables:**
- Add: `GOOGLE_API_KEY` = your actual API key

**Deploy:**
- Click **"Deploy"**
- Wait 3-5 minutes

## ✅ Test After Deployment

1. Visit your Vercel URL
2. Test health: `https://your-app.vercel.app/api/health`
3. Test query: Use browser console or the frontend

## 📝 Notes

- **First request**: May take 5-10 seconds (copies data to `/tmp`)
- **Subsequent requests**: Fast
- **Free tier timeout**: 10 seconds (may need Pro for 60s)
- **Auto-deploy**: Every `git push` redeploys automatically

## 🎉 Done!

Your app is live on Vercel with both frontend and backend!

