# Step-by-Step Vercel Deployment Guide

## 📋 Prerequisites Checklist

Before starting, make sure:
- [x] Your code is pushed to GitHub
- [x] You have a Google Gemini API key
- [x] Data files are committed (`data/vector_db/` and `data/storage/funds_database.json`)

---

## 🚀 Step 1: Sign Up / Login to Vercel

1. Go to **[vercel.com](https://vercel.com)**
2. Click **"Sign Up"** (or **"Log In"** if you already have an account)
3. **Recommended**: Sign up with **GitHub** (makes deployment easier)
   - Click **"Continue with GitHub"**
   - Authorize Vercel to access your repositories

**Why GitHub?** Vercel can automatically deploy from your GitHub repos and redeploy on every push.

---

## 📦 Step 2: Import Your Project

1. After logging in, you'll see the Vercel dashboard
2. Click **"Add New..."** button (top right)
3. Select **"Project"**
4. You'll see a list of your GitHub repositories
5. Find and click **"Import"** next to `rforrajat0995-cell/Milestone1`

**Why import?** This connects Vercel to your GitHub repo so it can build and deploy your code.

---

## ⚙️ Step 3: Configure Project Settings

After clicking "Import", you'll see the **"Configure Project"** page. Here's what to fill:

### 3.1 Framework Preset

**Field**: Framework Preset  
**Value**: Leave as **"Other"** or select **"Vite"** (both work)

**Why?** Vercel tries to auto-detect your framework. Since we have a custom setup (Python backend + React frontend), "Other" is fine.

---

### 3.2 Root Directory

**Field**: Root Directory  
**Value**: Leave **empty** (default)

**Why?** Your project root is the repository root. Leaving it empty tells Vercel to use the root directory.

---

### 3.3 Build and Output Settings

**Field**: Build Command  
**Value**: `cd frontend && npm install && npm run build`

**Why?** 
- `cd frontend` - Navigate to the frontend directory
- `npm install` - Install all Node.js dependencies (React, Vite, etc.)
- `npm run build` - Build the React app into static files

**Field**: Output Directory  
**Value**: `frontend/dist`

**Why?** This is where Vite builds your React app. Vercel needs to know where to find the built files to serve them.

**Field**: Install Command  
**Value**: Leave as **default** (`npm install`)

**Why?** Vercel will run this in the root directory. Since we're running `npm install` in the build command, this is fine.

---

### 3.4 Environment Variables

**This is CRITICAL!**

Click **"Environment Variables"** section to expand it.

**Add this variable:**

| Variable Name | Value | Environments |
|--------------|-------|--------------|
| `GOOGLE_API_KEY` | Your actual Google Gemini API key | ✅ Production<br>✅ Preview<br>✅ Development |

**Steps:**
1. Click **"Add"** button
2. **Name**: `GOOGLE_API_KEY`
3. **Value**: Paste your actual API key (e.g., `AIzaSy...your_key_here`)
4. **Environments**: Check all three boxes:
   - ✅ Production
   - ✅ Preview  
   - ✅ Development
5. Click **"Save"**

**Why is this needed?**
- Your Python backend uses Google Gemini API for embeddings and LLM
- Without this, the RAG system won't work
- Setting it for all environments ensures it works in production, preview, and development

**Where to get the API key?**
- Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
- Sign in with Google
- Click "Create API Key"
- Copy the key

---

## 🚀 Step 4: Deploy

1. Scroll down to the bottom of the page
2. Review your settings:
   - ✅ Build Command: `cd frontend && npm install && npm run build`
   - ✅ Output Directory: `frontend/dist`
   - ✅ Environment Variable: `GOOGLE_API_KEY` (set)
3. Click the big **"Deploy"** button

**What happens next?**
- Vercel will:
  1. Clone your repository
  2. Install Python dependencies (from `requirements.txt`)
  3. Install Node.js dependencies (from `frontend/package.json`)
  4. Build your frontend
  5. Set up Python serverless functions in `api/` directory
  6. Deploy everything

**Time**: This takes **3-5 minutes** for the first deployment.

---

## ⏳ Step 5: Wait for Build

You'll see a build log showing:
- ✅ Installing dependencies
- ✅ Building frontend
- ✅ Setting up Python functions
- ✅ Deploying

**Don't close the page!** You can watch the progress.

---

## ✅ Step 6: Verify Deployment

Once deployment completes, you'll see:

### 6.1 Your Deployment URL

Vercel will show you a URL like:
- `https://milestone1-xyz123.vercel.app`

**This is your live app!**

### 6.2 Test the Health Endpoint

1. Open a new browser tab
2. Visit: `https://your-app-url.vercel.app/api/health`
3. You should see:
   ```json
   {
     "status": "healthy",
     "service": "Mutual Fund FAQ Assistant (RAG)",
     "rag_ready": true,
     "platform": "Vercel"
   }
   ```

**Why test this?** This confirms your backend is working.

### 6.3 Test the Frontend

1. Visit: `https://your-app-url.vercel.app`
2. You should see your React chat interface
3. Try asking a question like: "What is the exit load for Parag Parikh ELSS?"

**Why test this?** This confirms your frontend is connected to the backend.

---

## 🎯 Step 7: Set Up Auto-Deploy (Optional but Recommended)

Vercel automatically sets this up, but verify:

1. Go to your project dashboard
2. Click **"Settings"** tab
3. Click **"Git"** in the sidebar
4. Verify:
   - ✅ **Production Branch**: `main` (or `master`)
   - ✅ **Auto-deploy**: Enabled

**Why?** Every time you push to GitHub, Vercel will automatically redeploy your app with the latest changes.

---

## 📊 Summary: All Fields Explained

| Field | Value | Why Needed |
|-------|-------|------------|
| **Framework Preset** | "Other" or "Vite" | Tells Vercel how to build (we have custom setup) |
| **Root Directory** | Empty | Uses repo root |
| **Build Command** | `cd frontend && npm install && npm run build` | Builds React frontend into static files |
| **Output Directory** | `frontend/dist` | Where Vercel finds built frontend files |
| **Install Command** | `npm install` (default) | Installs Node.js dependencies |
| **Environment Variable** | `GOOGLE_API_KEY` = your key | Required for Gemini API (embeddings + LLM) |

---

## ⚠️ Important Notes

### Timeout Limits

- **Free Tier**: 10 seconds max per request
- **Pro Tier**: 60 seconds max per request ($20/month)

**First request may take 5-10 seconds** (copies data to `/tmp`). If you hit timeouts:
- Upgrade to Pro tier
- Or optimize initialization

### Memory Limits

- **Free Tier**: 1024MB
- **Pro Tier**: 3008MB

If you get "out of memory" errors, upgrade to Pro.

### Cold Starts

- **First request after inactivity**: 5-10 seconds (copies data)
- **Subsequent requests**: Fast (< 1 second)

This is normal for serverless functions.

---

## 🐛 Troubleshooting

### Issue: Build fails with "Module not found"

**Solution**: Make sure `frontend/package.json` exists and has all dependencies.

### Issue: "GOOGLE_API_KEY not set"

**Solution**: 
- Go to Project Settings → Environment Variables
- Verify `GOOGLE_API_KEY` is set for all environments
- Redeploy

### Issue: "Function timeout"

**Solution**: 
- First request takes longer (normal)
- If persistent, upgrade to Pro tier (60s timeout)

### Issue: Frontend shows but backend doesn't work

**Solution**:
- Check `/api/health` endpoint
- Check Vercel function logs (in dashboard)
- Verify `GOOGLE_API_KEY` is set

### Issue: "Vector DB not found"

**Solution**:
- Ensure `data/vector_db/` is committed to Git
- Check `.gitignore` doesn't exclude it
- Rebuild locally and commit: `python build_rag_index.py && git add data/vector_db/ && git commit -m "Add vector DB" && git push`

---

## 🎉 You're Done!

Your app is now live on Vercel:
- **Frontend**: `https://your-app.vercel.app`
- **Backend API**: `https://your-app.vercel.app/api/*`

Every `git push` will automatically redeploy! 🚀

---

## 📝 Quick Reference

**Deploy URL**: `https://vercel.com/dashboard`  
**Project Settings**: Click your project → Settings  
**Environment Variables**: Settings → Environment Variables  
**View Logs**: Click your project → Deployments → Click a deployment → Functions tab

---

## 🔄 Updating Your App

To update your app:

1. Make changes locally
2. Commit and push:
   ```bash
   git add .
   git commit -m "Your changes"
   git push origin main
   ```
3. Vercel automatically redeploys (watch in dashboard)

That's it! No manual deployment needed. 🎊

