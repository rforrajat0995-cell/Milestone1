# Deploy Everything on Vercel - Complete Guide

This guide shows how to deploy both frontend and backend on Vercel.

## 🎯 Overview

- **Frontend**: React/Vite → Vercel (static build)
- **Backend**: Flask API → Vercel (serverless functions)
- **Data**: Pre-built vector DB committed to Git
- **Total Cost**: Free (Vercel free tier)

## 📋 Prerequisites

- GitHub repository (already done ✅)
- Vercel account (free tier)
- Google Gemini API key
- Pre-built data (vector DB and funds database)

---

## 🔧 Step 1: Pre-build Data Locally

Before deploying, build the data locally:

```bash
cd /Users/binoykrishna/Milestone1

# Activate virtual environment
source venv/bin/activate

# Build the data
python main.py
python build_rag_index.py
```

This creates:
- `data/storage/funds_database.json`
- `data/vector_db/` (vector database)

---

## 📦 Step 2: Commit Data Files

The vector DB needs to be in Git for Vercel to access it:

```bash
# Add data files
git add data/storage/funds_database.json
git add data/vector_db/

# Commit
git commit -m "Add pre-built data for Vercel deployment"

# Push
git push origin main
```

**Note**: This will increase your repo size, but it's necessary for Vercel deployment.

---

## 🚀 Step 3: Deploy to Vercel

### 3.1 Sign Up for Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click **"Sign Up"**
3. Sign up with **GitHub** (recommended)

### 3.2 Import Project

1. Click **"Add New..."** → **"Project"**
2. Import your GitHub repository: `rforrajat0995-cell/Milestone1`
3. Click **"Import"**

### 3.3 Configure Project Settings

**Framework Preset**: Leave as "Other" or "Vite"

**Root Directory**: Leave empty (uses root)

**Build Settings**:
- **Build Command**: `cd frontend && npm install && npm run build`
- **Output Directory**: `frontend/dist`
- **Install Command**: `npm install` (for frontend)

**Note**: Vercel will auto-detect Python functions in `api/` directory.

### 3.4 Add Environment Variables

1. Scroll to **"Environment Variables"** section
2. Click **"Add"**
3. Add:
   - **Key**: `GOOGLE_API_KEY`
   - **Value**: Your actual Google Gemini API key
   - **Environment**: Production, Preview, Development (select all)
4. Click **"Save"**

### 3.5 Deploy

1. Scroll to bottom
2. Click **"Deploy"**
3. Wait 3-5 minutes for build to complete

---

## ✅ Step 4: Verify Deployment

### 4.1 Test Health Endpoint

Visit: `https://your-app.vercel.app/api/health`

Should return:
```json
{
  "status": "healthy",
  "service": "Mutual Fund FAQ Assistant (RAG)",
  "rag_ready": true,
  "platform": "Vercel"
}
```

### 4.2 Test Query Endpoint

Using browser console or curl:
```javascript
fetch('/api/query', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({query: 'What is the exit load for Parag Parikh ELSS?'})
})
.then(r => r.json())
.then(console.log)
```

### 4.3 Test Frontend

Visit: `https://your-app.vercel.app`

The frontend should load and connect to the backend automatically.

---

## ⚠️ Important Notes

### Cold Starts

- **First request**: 5-10 seconds (copies data to `/tmp`)
- **Subsequent requests**: Fast (data cached in `/tmp`)
- **After inactivity**: Data may be lost (first request will re-copy)

### Timeout Limits

- **Free tier**: 10 seconds
- **Pro tier**: 60 seconds (recommended for RAG)

If you hit timeouts, consider:
- Upgrading to Pro ($20/month)
- Optimizing initialization
- Using external vector DB (Pinecone, etc.)

### Memory Limits

- **Free tier**: 1024MB
- **Pro tier**: 3008MB

The RAG system with sentence-transformers may need Pro tier.

---

## 🔄 Updating Data

If you need to update the data:

1. **Rebuild locally**:
   ```bash
   python main.py
   python build_rag_index.py
   ```

2. **Commit and push**:
   ```bash
   git add data/
   git commit -m "Update fund data"
   git push
   ```

3. **Vercel will auto-redeploy** with new data

---

## 🐛 Troubleshooting

### Issue: "Function timeout"

**Solution**: 
- Upgrade to Pro tier (60s timeout)
- Or optimize initialization

### Issue: "Memory limit exceeded"

**Solution**:
- Upgrade to Pro tier
- Or use external vector DB

### Issue: "Vector DB not found"

**Solution**:
- Ensure `data/vector_db/` is committed to Git
- Check `.gitignore` doesn't exclude it
- Rebuild and commit data

### Issue: "RAG pipeline not initialized"

**Solution**:
- Check `GOOGLE_API_KEY` is set in Vercel
- Check logs for initialization errors
- First request takes longer (normal)

---

## 📊 Project Structure

```
Milestone1/
├── api/                    # Vercel serverless functions
│   ├── query.py           # Query endpoint
│   ├── health.py          # Health check
│   └── funds.py           # List funds
├── frontend/              # React frontend
│   ├── src/
│   └── package.json
├── data/
│   ├── storage/
│   │   └── funds_database.json  # Committed to Git
│   └── vector_db/         # Committed to Git (for Vercel)
├── vercel.json            # Vercel configuration
└── ... (other files)
```

---

## ✅ Checklist

Before deploying:
- [ ] Data pre-built locally (`python main.py && python build_rag_index.py`)
- [ ] Data files committed to Git
- [ ] `.gitignore` allows `data/vector_db/`
- [ ] Vercel account created
- [ ] `GOOGLE_API_KEY` ready

After deploying:
- [ ] Health endpoint works
- [ ] Query endpoint works
- [ ] Frontend loads
- [ ] Frontend connects to backend
- [ ] Queries return answers

---

## 🎉 You're Done!

Your app is now fully deployed on Vercel:
- **Frontend**: `https://your-app.vercel.app`
- **Backend API**: `https://your-app.vercel.app/api/*`

Every `git push` will automatically redeploy! 🚀

