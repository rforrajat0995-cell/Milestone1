# Hybrid Deployment: Step-by-Step Guide

**Frontend on Vercel + Backend on Render**

This is the recommended approach for best performance and reliability.

---

## 🎯 Overview

- **Backend**: Render (free tier, persistent storage)
- **Frontend**: Vercel (free tier, fast CDN)
- **Total Cost**: $0/month (free tier on both)

---

## 📋 Part 1: Deploy Backend to Render

### Step 1: Sign Up for Render

1. Go to **[render.com](https://render.com)**
2. Click **"Get Started for Free"**
3. Sign up with **GitHub** (recommended - easier integration)

### Step 2: Create New Web Service

1. Once logged in, click **"New +"** button (top right)
2. Select **"Web Service"**
3. If not connected, click **"Connect GitHub"**
4. Authorize Render to access your repositories
5. Select your repository: **`rforrajat0995-cell/Milestone1`**
6. Click **"Connect"**

### Step 3: Configure Service Settings

Fill in the configuration form:

- **Name**: `mutual-fund-faq-backend` (or your choice)
- **Region**: Choose closest to you (e.g., `Oregon (US West)`)
- **Branch**: `main`
- **Root Directory**: Leave **empty** (uses root directory)
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python backend_rag_api.py`
- **Plan**: Select **"Free"** (or "Starter" for $7/month - no spin-downs)

### Step 4: Add Environment Variables

1. Scroll down to **"Environment Variables"** section
2. Click **"Add Environment Variable"**
3. Add these variables one by one:

   **Variable 1:**
   - Key: `GOOGLE_API_KEY`
   - Value: `your_actual_google_api_key_here` (paste your real API key)
   - Click **"Save"**

   **Variable 2:**
   - Key: `PORT`
   - Value: `5000`
   - Click **"Save"**

   **Variable 3:**
   - Key: `FLASK_DEBUG`
   - Value: `False`
   - Click **"Save"**

### Step 5: Deploy

1. Scroll to the bottom of the page
2. Click **"Create Web Service"**
3. Render will start building and deploying
4. **Wait 5-10 minutes** for the first deployment

### Step 6: Get Your Backend URL

1. Once deployment completes, you'll see a URL like:
   `https://mutual-fund-faq-backend.onrender.com`
2. **Copy this URL** - you'll need it for the frontend
3. Test it: Open the URL in browser, you should see an error (that's OK - it means it's running)

### Step 7: Test Backend Health

1. Go to: `https://your-backend-url.onrender.com/health`
2. You should see:
   ```json
   {
     "status": "healthy",
     "service": "Mutual Fund FAQ Assistant (RAG)",
     "rag_ready": false
   }
   ```
   (rag_ready might be false initially - we'll fix that in next step)

### Step 8: Initialize Data (IMPORTANT!)

Since `data/vector_db/` is not in Git, you need to initialize it on Render:

**Method 1: Using Render Shell (Recommended)**

1. In your Render dashboard, go to your service
2. Click on the **"Shell"** tab (in the left sidebar)
3. Wait for the shell to open
4. Run these commands one by one:

   ```bash
   python main.py
   ```
   (This will scrape the mutual fund data - takes 2-3 minutes)

   ```bash
   python build_rag_index.py
   ```
   (This will build the RAG index - takes 1-2 minutes)

5. Once both complete, your backend is ready!

**Method 2: Using Render CLI (Alternative)**

1. Install Render CLI:
   ```bash
   npm install -g render-cli
   ```

2. Login:
   ```bash
   render login
   ```

3. Run commands:
   ```bash
   render exec mutual-fund-faq-backend -- python main.py
   render exec mutual-fund-faq-backend -- python build_rag_index.py
   ```

### Step 9: Verify Backend is Working

1. Go to: `https://your-backend-url.onrender.com/health`
2. Now you should see:
   ```json
   {
     "status": "healthy",
     "service": "Mutual Fund FAQ Assistant (RAG)",
     "rag_ready": true
   }
   ```

3. Test a query (using curl or Postman):
   ```bash
   curl -X POST https://your-backend-url.onrender.com/query \
     -H "Content-Type: application/json" \
     -d '{"query": "What is the exit load for Parag Parikh ELSS?"}'
   ```

✅ **Backend is now deployed!**

---

## ⚡ Part 2: Deploy Frontend to Vercel

### Step 1: Sign Up for Vercel

1. Go to **[vercel.com](https://vercel.com)**
2. Click **"Sign Up"**
3. Sign up with **GitHub** (recommended - easier integration)

### Step 2: Import Project

1. Once logged in, click **"Add New..."** button (top right)
2. Select **"Project"**
3. Click **"Import Git Repository"**
4. Find and select: **`rforrajat0995-cell/Milestone1`**
5. Click **"Import"**

### Step 3: Configure Project Settings

Vercel should auto-detect Vite, but verify/configure:

1. **Framework Preset**: `Vite` (should be auto-detected)
2. **Root Directory**: Click **"Edit"** → Set to `frontend`
3. **Build Command**: `npm install && npm run build`
4. **Output Directory**: `dist`
5. **Install Command**: `npm install`

### Step 4: Add Environment Variable

1. Scroll down to **"Environment Variables"** section
2. Click **"Add"**
3. Add:
   - **Key**: `VITE_API_BASE_URL`
   - **Value**: `https://your-render-backend-url.onrender.com` 
     (Replace with your actual Render backend URL from Part 1, Step 6)
4. Click **"Save"**

### Step 5: Deploy

1. Scroll to bottom
2. Click **"Deploy"**
3. Wait 1-2 minutes for build to complete
4. Vercel will provide a URL like: `https://your-app.vercel.app`

### Step 6: Verify Frontend is Working

1. Visit your Vercel URL
2. You should see the chat interface
3. Check browser console (F12) for any errors
4. The frontend should show "Backend Connected" if everything is working

### Step 7: Test the Full Application

1. Type a query: "What's the exit load for Parag Parikh Arbitrage Fund?"
2. Click send
3. You should get a response with source URL

✅ **Frontend is now deployed!**

---

## 🔄 Part 3: Auto-Deployment Setup

Both platforms are already configured for auto-deployment:

- **Render**: Automatically deploys when you push to `main` branch
- **Vercel**: Automatically deploys when you push to `main` branch

### Making Changes

1. Make changes locally
2. Test locally (optional)
3. Commit and push:
   ```bash
   git add .
   git commit -m "Your change description"
   git push origin main
   ```
4. Both Render and Vercel will automatically redeploy! 🎉

---

## 🐛 Troubleshooting

### Backend Issues

**Problem: "rag_ready: false"**
- **Solution**: Run initialization commands in Render Shell (Step 8 above)

**Problem: "Service spins down after 15 minutes"**
- **Solution**: This is normal for Render free tier
- First request after inactivity takes 30-60 seconds
- Upgrade to Starter plan ($7/month) to avoid spin-downs

**Problem: "Module not found"**
- **Solution**: Check that `requirements.txt` is in root directory
- Verify build logs in Render dashboard

**Problem: "Port already in use"**
- **Solution**: Backend already uses `os.getenv('PORT')` - this should work automatically

### Frontend Issues

**Problem: "Backend not connected"**
- **Solution**: 
  1. Check `VITE_API_BASE_URL` in Vercel environment variables
  2. Ensure backend URL is correct (no trailing slash)
  3. Test backend health endpoint directly

**Problem: "CORS errors"**
- **Solution**: Backend already has CORS configured - check Render logs if issues persist

**Problem: "Build failed"**
- **Solution**: 
  1. Check Vercel build logs
  2. Ensure `frontend/package.json` exists
  3. Verify Node.js version (Vercel auto-detects)

### Data Issues

**Problem: "No funds found"**
- **Solution**: Run `python main.py` in Render Shell

**Problem: "Vector DB not found"**
- **Solution**: Run `python build_rag_index.py` in Render Shell

---

## 📊 Monitoring

### Render Monitoring

- **Logs**: Render Dashboard → Your Service → Logs tab
- **Metrics**: Render Dashboard → Metrics (CPU, Memory, Network)
- **Events**: Render Dashboard → Events (deployment history)

### Vercel Monitoring

- **Logs**: Vercel Dashboard → Your Project → Deployments → View Logs
- **Analytics**: Vercel Dashboard → Analytics (page views, performance)
- **Speed Insights**: Enable in project settings

---

## 💰 Cost

- **Render (Backend)**: Free (with 15-min spin-down) or $7/month (Starter - no spin-down)
- **Vercel (Frontend)**: Free (unlimited for personal projects)
- **Total**: $0/month (free tier) or $7/month (if you upgrade Render)

---

## ✅ Checklist

### Backend (Render)
- [ ] Signed up for Render
- [ ] Created web service
- [ ] Added environment variables (GOOGLE_API_KEY, PORT, FLASK_DEBUG)
- [ ] Deployed successfully
- [ ] Initialized data (main.py + build_rag_index.py)
- [ ] Tested /health endpoint
- [ ] Backend URL copied

### Frontend (Vercel)
- [ ] Signed up for Vercel
- [ ] Imported project from GitHub
- [ ] Configured build settings (root: frontend)
- [ ] Added environment variable (VITE_API_BASE_URL)
- [ ] Deployed successfully
- [ ] Tested frontend URL
- [ ] Verified backend connection

### Testing
- [ ] Backend health check works
- [ ] Frontend loads correctly
- [ ] Can send queries
- [ ] Receives responses with source URLs
- [ ] No console errors

---

## 🎉 You're Done!

Your application is now live:
- **Frontend**: `https://your-app.vercel.app`
- **Backend**: `https://your-backend.onrender.com`

Every `git push` will automatically redeploy both! 🚀

---

## 🆘 Need Help?

- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **Project Issues**: Check GitHub issues

