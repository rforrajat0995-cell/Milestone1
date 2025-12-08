# Quick Vercel Deployment Checklist

## Pre-Deployment ✅

- [x] Code is committed and pushed to GitHub
- [x] `vercel.json` is configured correctly
- [x] `requirements.txt` has all Python dependencies
- [x] `frontend/package.json` has all npm dependencies

## Step-by-Step Deployment

### 1. Create Vercel Project
- [ ] Go to [vercel.com](https://vercel.com) and sign in
- [ ] Click **"Add New..."** → **"Project"**
- [ ] Import your **Milestone1** repository from GitHub
- [ ] Click **"Import"**

### 2. Configure Settings
- [ ] **Framework Preset:** Select **"Other"**
- [ ] **Root Directory:** Leave **empty**
- [ ] **Build Command:** Leave **empty** (handled by vercel.json)
- [ ] **Output Directory:** Leave **empty** (handled by vercel.json)

### 3. Add Environment Variables
Click **"Environment Variables"** and add:

- [ ] **Name:** `GOOGLE_API_KEY`
  - **Value:** Your Google Gemini API key (from [aistudio.google.com](https://aistudio.google.com/app/apikey))
  - **Environments:** ✅ Production, ✅ Preview, ✅ Development

- [ ] **Name:** `VECTOR_DB_PATH`
  - **Value:** `/tmp/vector_db`
  - **Environments:** ✅ Production, ✅ Preview, ✅ Development

### 4. Deploy
- [ ] Click **"Deploy"** button
- [ ] Wait for build to complete (3-5 minutes)
- [ ] Check build logs for any errors

### 5. Verify Deployment
- [ ] Visit your deployment URL (e.g., `milestone1-xyz.vercel.app`)
- [ ] Check frontend loads correctly
- [ ] Test `/api/health` endpoint: `https://your-app.vercel.app/api/health`
- [ ] Should return: `{"status":"healthy","service":"Mutual Fund FAQ Assistant (RAG)"}`
- [ ] Test a query in the frontend

## Common Issues

### ❌ 404 Error
**Fix:** Check that `vercel.json` routes are correct (already configured)

### ❌ Backend not connected
**Fix:** 
1. Check `/api/health` endpoint directly
2. Verify `GOOGLE_API_KEY` is set
3. Check function logs in Vercel dashboard

### ❌ Build fails
**Fix:**
1. Check build logs for specific errors
2. Verify all dependencies are in `requirements.txt` and `package.json`
3. Check Python version (should be 3.12)

### ❌ API Key error
**Fix:**
1. Verify `GOOGLE_API_KEY` in environment variables
2. **Redeploy** after adding env vars (Vercel will prompt you)

## Quick Test Commands

After deployment, test these URLs:

```bash
# Health check
curl https://your-app.vercel.app/api/health

# Should return:
# {"status":"healthy","service":"Mutual Fund FAQ Assistant (RAG)","rag_ready":true}
```

## Important Notes

- ⏱️ **First query may take 10-20 seconds** (cold start + data initialization)
- 🔄 **Subsequent queries are faster** (warm functions)
- 📊 **Monitor usage** in Vercel dashboard → Functions tab
- 🔑 **Keep API key secure** - never commit it to GitHub

## Need Help?

1. Check `VERCEL_DEPLOYMENT_GUIDE.md` for detailed explanations
2. Check Vercel function logs in dashboard
3. Test endpoints directly with curl or browser

---

**Ready to deploy?** Follow the checklist above step by step! 🚀

