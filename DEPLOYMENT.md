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
│ Backend (Render)│
│ Flask API        │
│ + Vector DB     │
│ + Data Storage  │
└─────────────────┘
```

## 📋 Prerequisites

- GitHub repository (already done ✅)
- Render account (free tier available) - **Recommended**
- OR Railway account (paid plan required for web services)
- Vercel account (free tier available)
- Google Gemini API key

---

## 🚀 Part 1: Deploy Backend to Render (Recommended - Free Tier)

### Step 1: Sign Up for Render

1. Go to [render.com](https://render.com)
2. Click **"Get Started for Free"**
3. Sign up with GitHub (recommended for easy integration)

### Step 2: Create New Web Service

1. Click **"New +"** → **"Web Service"**
2. Click **"Connect GitHub"** (if not already connected)
3. Select your repository: `rforrajat0995-cell/Milestone1`
4. Click **"Connect"**

### Step 3: Configure Service Settings

Fill in the following:

- **Name**: `mutual-fund-faq-backend` (or your choice)
- **Region**: Choose closest to you (e.g., `Oregon (US West)`)
- **Branch**: `main`
- **Root Directory**: Leave empty (root)
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python backend_rag_api.py`
- **Plan**: Select **"Free"** (or "Starter" for $7/month with better performance)

### Step 4: Configure Environment Variables

1. Scroll down to **"Environment Variables"** section
2. Click **"Add Environment Variable"**
3. Add the following:

   ```
   GOOGLE_API_KEY = your_actual_google_api_key_here
   PORT = 5000
   FLASK_DEBUG = False
   ```

4. Click **"Save Changes"**

### Step 5: Deploy

1. Scroll to bottom
2. Click **"Create Web Service"**
3. Render will start building and deploying (takes 5-10 minutes)

### Step 6: Initialize Data (Important!)

Since `data/vector_db/` is not in Git, you need to initialize it on Render:

**Option A: Using Render Shell (Recommended)**

1. Once deployment is live, go to your service
2. Click **"Shell"** tab
3. Run these commands:
   ```bash
   python main.py
   python build_rag_index.py
   ```

**Option B: Add to Startup Script**

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

### Step 7: Get Your Backend URL

1. Once deployed, Render will provide a URL like:
   `https://mutual-fund-faq-backend.onrender.com`
2. Copy this URL - you'll need it for the frontend
3. Test the backend:
   ```bash
   curl https://mutual-fund-faq-backend.onrender.com/health
   ```

### Step 8: Verify Backend is Working

1. Go to: `https://your-app-name.onrender.com/health`
2. You should see:
   ```json
   {
     "status": "healthy",
     "service": "Mutual Fund FAQ Assistant (RAG)",
     "rag_ready": true
   }
   ```

**Note**: Free tier services on Render spin down after 15 minutes of inactivity. First request may take 30-60 seconds to wake up.

---

## 🚂 Alternative: Deploy Backend to Railway (Paid Plan Required)

If you prefer Railway, you'll need to upgrade to a paid plan ($5/month minimum):

1. Go to [railway.app](https://railway.app)
2. Upgrade your account (Hobby plan: $5/month)
3. Follow the same steps as Render above
4. Railway doesn't have the spin-down issue like Render's free tier

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
   VITE_API_BASE_URL=https://your-render-backend-url.onrender.com
   ```
   (Replace with your actual Render backend URL)

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

### Render Auto-Deploy

Render automatically deploys when you push to GitHub:
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
- Solution: Render sets PORT automatically, ensure backend uses `os.getenv('PORT')`

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

### Render Monitoring

1. **Logs**: Render Dashboard → Your Service → Logs tab
2. **Metrics**: Render Dashboard → Metrics (CPU, Memory, Network)
3. **Events**: Render Dashboard → Events (deployment history)

### Vercel Monitoring

1. **Logs**: Vercel Dashboard → Project → Deployments → View Logs
2. **Analytics**: Vercel Dashboard → Analytics (page views, performance)
3. **Speed Insights**: Enable in project settings

---

## 💰 Cost Estimation

### Render (Backend)
- **Free Tier**: Free forever (with 15-min spin-down after inactivity)
- **Starter Plan**: $7/month (no spin-downs, better performance)
- **Estimated Usage**: $0/month (free tier) or $7/month (starter)

### Vercel (Frontend)
- **Free Tier**: Unlimited for personal projects
- **Pro Plan**: $20/month (only if you need team features)
- **Estimated Usage**: $0/month for personal use

**Total Estimated Cost: $0/month (free tier) or $7/month (starter plan)** 🎉

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

- **Render Docs**: https://render.com/docs
- **Railway Docs**: https://docs.railway.app (if using paid plan)
- **Vercel Docs**: https://vercel.com/docs
- **Project Issues**: Check GitHub issues or create a new one

---

**Congratulations! 🎉 Your application is now live in production!**

