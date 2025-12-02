# Deployment Guide

Complete step-by-step guide to deploy the Mutual Fund FAQ Assistant to production.

## 🏗️ Architecture

```
┌─────────────────┐
│  Frontend       │
│  (Vercel)       │
│  React/Vite     │
└────────┬────────┘
         │ API Calls
         ▼
┌─────────────────┐
│ Backend (Railway)│
│ Flask API        │
│ + Vector DB     │
│ + Data Storage  │
└─────────────────┘
```

## 📋 Prerequisites

- GitHub repository (already done ✅)
- Railway account (free tier available)
- Vercel account (free tier available)
- Google Gemini API key

---

## 🚂 Part 1: Deploy Backend to Railway

### Step 1: Sign Up for Railway

1. Go to [railway.app](https://railway.app)
2. Click **"Start a New Project"** or **"Login"**
3. Sign up with GitHub (recommended for easy integration)

### Step 2: Create New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Authorize Railway to access your GitHub repositories
4. Select your repository: `rforrajat0995-cell/Milestone1`
5. Click **"Deploy Now"**

### Step 3: Configure Environment Variables

1. In your Railway project, go to **"Variables"** tab
2. Click **"New Variable"**
3. Add the following:

   ```
   GOOGLE_API_KEY=your_actual_google_api_key_here
   PORT=5000
   FLASK_DEBUG=False
   ```

4. Click **"Add"** for each variable

### Step 4: Configure Build Settings

Railway should auto-detect Python, but verify:

1. Go to **"Settings"** tab
2. **Build Command**: Leave empty (Railway auto-detects)
3. **Start Command**: `python backend_rag_api.py`
4. **Root Directory**: `/` (root)

### Step 5: Initialize Data (Important!)

Since `data/vector_db/` is not in Git, you need to initialize it on Railway:

**Option A: Using Railway CLI (Recommended)**

1. Install Railway CLI:
   ```bash
   npm i -g @railway/cli
   railway login
   ```

2. Link your project:
   ```bash
   railway link
   ```

3. Run initialization commands:
   ```bash
   railway run python main.py
   railway run python build_rag_index.py
   ```

**Option B: Using Railway Dashboard**

1. Go to your project on Railway
2. Click **"Deployments"** → **"View Logs"**
3. Use **"Run Command"** feature:
   - Command: `python main.py`
   - Then: `python build_rag_index.py`

**Option C: Add to Startup Script**

Create a file `init_data.sh`:

```bash
#!/bin/bash
if [ ! -f "data/storage/funds_database.json" ]; then
    echo "Initializing data..."
    python main.py
    python build_rag_index.py
fi
python backend_rag_api.py
```

Update `Procfile`:
```
web: bash init_data.sh
```

### Step 6: Get Your Backend URL

1. Once deployed, Railway will provide a URL like:
   `https://your-app-name.railway.app`
2. Copy this URL - you'll need it for the frontend
3. Test the backend:
   ```bash
   curl https://your-app-name.railway.app/health
   ```

### Step 7: Verify Backend is Working

1. Go to: `https://your-app-name.railway.app/health`
2. You should see:
   ```json
   {
     "status": "healthy",
     "service": "Mutual Fund FAQ Assistant (RAG)",
     "rag_ready": true
   }
   ```

---

## ⚡ Part 2: Deploy Frontend to Vercel

### Step 1: Sign Up for Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click **"Sign Up"**
3. Sign up with GitHub (recommended)

### Step 2: Import Project

1. Click **"Add New..."** → **"Project"**
2. Import your GitHub repository: `rforrajat0995-cell/Milestone1`
3. Click **"Import"**

### Step 3: Configure Build Settings

Vercel should auto-detect Vite, but configure manually:

1. **Framework Preset**: `Vite`
2. **Root Directory**: `frontend`
3. **Build Command**: `npm install && npm run build`
4. **Output Directory**: `dist`
5. **Install Command**: `npm install`

### Step 4: Add Environment Variables

1. In project settings, go to **"Environment Variables"**
2. Add:
   ```
   VITE_API_BASE_URL=https://your-railway-backend-url.railway.app
   ```
   (Replace with your actual Railway backend URL)

3. Click **"Save"**

### Step 5: Deploy

1. Click **"Deploy"**
2. Wait for build to complete (usually 1-2 minutes)
3. Vercel will provide a URL like: `https://your-app.vercel.app`

### Step 6: Verify Frontend is Working

1. Visit your Vercel URL
2. Check browser console for any errors
3. Test a query to ensure it connects to the backend

---

## 🔄 Part 3: Auto-Deployment Setup

### Railway Auto-Deploy

Railway automatically deploys when you push to GitHub:
- ✅ Already configured when you connected GitHub
- Every `git push` triggers a new deployment

### Vercel Auto-Deploy

Vercel automatically deploys when you push to GitHub:
- ✅ Already configured when you imported the project
- Every `git push` triggers a new deployment

### Making Changes After Deployment

1. **Make code changes locally**
2. **Test locally** (optional but recommended)
3. **Commit and push:**
   ```bash
   git add .
   git commit -m "Your change description"
   git push origin main
   ```
4. **Railway and Vercel will automatically redeploy** 🎉

---

## 🐛 Troubleshooting

### Backend Issues

**Problem: "RAG pipeline not initialized"**
- Solution: Run `python build_rag_index.py` on Railway
- Check logs: Railway Dashboard → Deployments → View Logs

**Problem: "No module named 'chromadb'"**
- Solution: Verify `requirements.txt` is in root directory
- Railway should auto-install, but check build logs

**Problem: "Port already in use"**
- Solution: Railway sets PORT automatically, ensure backend uses `os.getenv('PORT')`

**Problem: "Vector DB not found"**
- Solution: Initialize data using one of the methods in Step 5 above

### Frontend Issues

**Problem: "Backend not connected"**
- Solution: Check `VITE_API_BASE_URL` in Vercel environment variables
- Ensure backend URL is correct (no trailing slash)
- Check CORS settings in `backend_rag_api.py`

**Problem: "Build failed"**
- Solution: Check Vercel build logs
- Ensure `frontend/package.json` exists
- Verify Node.js version (Vercel auto-detects)

**Problem: "CORS errors"**
- Solution: Backend already has `CORS(app, resources={r"/*": {"origins": "*"}})`
- If issues persist, check Railway logs

### Data Issues

**Problem: "No funds found"**
- Solution: Run `python main.py` on Railway to scrape data
- Then run `python build_rag_index.py` to build index

**Problem: "Vector DB corrupted"**
- Solution: Delete `data/vector_db/` on Railway
- Re-run `python build_rag_index.py`

---

## 📊 Monitoring

### Railway Monitoring

1. **Logs**: Railway Dashboard → Deployments → View Logs
2. **Metrics**: Railway Dashboard → Metrics (CPU, Memory, Network)
3. **Alerts**: Set up alerts for deployment failures

### Vercel Monitoring

1. **Logs**: Vercel Dashboard → Project → Deployments → View Logs
2. **Analytics**: Vercel Dashboard → Analytics (page views, performance)
3. **Speed Insights**: Enable in project settings

---

## 💰 Cost Estimation

### Railway (Backend)
- **Free Tier**: $5 credit/month
- **Hobby Plan**: $5/month (if you exceed free tier)
- **Estimated Usage**: ~$0-5/month for low traffic

### Vercel (Frontend)
- **Free Tier**: Unlimited for personal projects
- **Pro Plan**: $20/month (only if you need team features)
- **Estimated Usage**: $0/month for personal use

**Total Estimated Cost: $0-5/month** 🎉

---

## 🔐 Security Checklist

- [x] `.env` files are gitignored
- [x] API keys stored as environment variables
- [x] CORS configured properly
- [x] No hardcoded credentials
- [x] HTTPS enabled (automatic on Railway/Vercel)

---

## 📝 Next Steps After Deployment

1. **Test the deployed application**
2. **Set up custom domain** (optional):
   - Railway: Settings → Domains
   - Vercel: Settings → Domains
3. **Monitor usage and performance**
4. **Set up error tracking** (optional):
   - Sentry
   - LogRocket
5. **Set up analytics** (optional):
   - Google Analytics
   - Vercel Analytics

---

## 🆘 Need Help?

- **Railway Docs**: https://docs.railway.app
- **Vercel Docs**: https://vercel.com/docs
- **Project Issues**: Check GitHub issues or create a new one

---

**Congratulations! 🎉 Your application is now live in production!**

