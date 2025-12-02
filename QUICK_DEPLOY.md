# Quick Deployment Checklist

## 🚀 Fast Track Deployment (15 minutes)

### Backend (Railway) - 5 minutes

1. ✅ Go to [railway.app](https://railway.app) → Sign up with GitHub
2. ✅ New Project → Deploy from GitHub → Select `rforrajat0995-cell/Milestone1`
3. ✅ Variables tab → Add:
   - `GOOGLE_API_KEY=your_key`
   - `PORT=5000`
4. ✅ Settings → Start Command: `python backend_rag_api.py`
5. ✅ Copy backend URL (e.g., `https://xxx.railway.app`)
6. ✅ Initialize data: Railway CLI → `railway run python main.py && railway run python build_rag_index.py`

### Frontend (Vercel) - 5 minutes

1. ✅ Go to [vercel.com](https://vercel.com) → Sign up with GitHub
2. ✅ Add New Project → Import `rforrajat0995-cell/Milestone1`
3. ✅ Configure:
   - Root Directory: `frontend`
   - Build Command: `npm install && npm run build`
   - Output Directory: `dist`
4. ✅ Environment Variables:
   - `VITE_API_BASE_URL=https://xxx.railway.app` (your Railway URL)
5. ✅ Deploy → Copy frontend URL

### Test - 2 minutes

1. ✅ Visit frontend URL
2. ✅ Test query: "What's the exit load of Parag Parikh Arbitrage Fund?"
3. ✅ Check backend health: `https://xxx.railway.app/health`

## 🎉 Done!

Your app is live! Every `git push` will auto-deploy.

---

**Full guide**: See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

