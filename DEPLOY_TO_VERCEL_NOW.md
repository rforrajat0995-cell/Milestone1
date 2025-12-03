# Deploy to Vercel - Final Checklist

## ✅ Pre-Deployment Checklist

Before deploying, verify:

- [x] New API key generated and added to `.env` file
- [x] All code committed to GitHub
- [x] `data/storage/funds_database.json` exists and is committed
- [x] `data/vector_db/` directory exists and is committed
- [x] `vercel.json` is configured correctly
- [x] `api/` directory has serverless functions
- [x] Frontend is ready to build

## 🚀 Deployment Steps

### Step 1: Go to Vercel

1. Visit **[vercel.com](https://vercel.com)**
2. **Sign up** or **Log in** (use GitHub for easiest setup)

### Step 2: Import Project

1. Click **"Add New..."** → **"Project"**
2. You'll see your GitHub repositories
3. Find **`rforrajat0995-cell/Milestone1`**
4. Click **"Import"**

### Step 3: Configure Project Settings

**Framework Preset**: Leave as **"Other"** (or select "Vite")

**Root Directory**: Leave **empty** (uses repo root)

**Build Command**: 
```
cd frontend && npm install && npm run build
```

**Output Directory**: 
```
frontend/dist
```

**Install Command**: Leave as default (`npm install`)

### Step 4: Add Environment Variable (CRITICAL!)

1. Scroll to **"Environment Variables"** section
2. Click **"Add"**
3. Fill in:
   - **Name**: `GOOGLE_API_KEY`
   - **Value**: Your **NEW** API key (the one you just added to `.env`)
   - **Environments**: Check **ALL THREE**:
     - ✅ Production
     - ✅ Preview
     - ✅ Development
4. Click **"Save"**

⚠️ **IMPORTANT**: Use your NEW API key here, not the old one!

### Step 5: Deploy

1. Scroll to the bottom
2. Review your settings
3. Click the big **"Deploy"** button
4. Wait 3-5 minutes for the build to complete

## ✅ Post-Deployment Verification

### 1. Check Build Logs

In Vercel dashboard, watch the build logs:
- ✅ Installing dependencies
- ✅ Building frontend
- ✅ Setting up Python functions
- ✅ Deploying

### 2. Test Health Endpoint

Once deployed, visit:
```
https://your-app-name.vercel.app/api/health
```

You should see:
```json
{
  "status": "healthy",
  "service": "Mutual Fund FAQ Assistant (RAG)",
  "rag_ready": true,
  "platform": "Vercel"
}
```

### 3. Test Frontend

Visit:
```
https://your-app-name.vercel.app
```

You should see your chat interface.

### 4. Test a Query

Try asking: "What is the exit load for Parag Parikh ELSS?"

**Note**: First request may take 5-10 seconds (copies data to `/tmp`). Subsequent requests will be faster.

## 🐛 Troubleshooting

### Issue: Build fails with "No Output Directory"

**Solution**: 
- Verify **Output Directory** is set to `frontend/dist`
- Check that `vercel.json` has correct configuration
- See `VERCEL_BUILD_FIX.md` for details

### Issue: "RAG pipeline not initialized"

**Solution**:
- Check `GOOGLE_API_KEY` is set correctly in Vercel
- Check build logs for errors
- First request takes longer (normal)

### Issue: "Function timeout"

**Solution**:
- Free tier has 10-second timeout
- First request may take 5-10 seconds (normal)
- If persistent, consider upgrading to Pro ($20/month for 60s timeout)

### Issue: Frontend loads but backend doesn't work

**Solution**:
- Check `/api/health` endpoint
- Verify environment variables are set
- Check Vercel function logs

## 📝 Quick Reference

**Vercel Dashboard**: https://vercel.com/dashboard  
**Project Settings**: Your Project → Settings  
**Environment Variables**: Settings → Environment Variables  
**View Logs**: Your Project → Deployments → Click deployment → Functions tab

## 🎉 Success!

Once everything is working:
- ✅ Frontend: `https://your-app.vercel.app`
- ✅ Backend API: `https://your-app.vercel.app/api/*`
- ✅ Auto-deploy: Every `git push` redeploys automatically!

## 🔄 Updating After Deployment

To update your app:
1. Make changes locally
2. Commit and push:
   ```bash
   git add .
   git commit -m "Your changes"
   git push origin main
   ```
3. Vercel automatically redeploys!

---

**Ready to deploy?** Follow the steps above and you'll be live in 5 minutes! 🚀

