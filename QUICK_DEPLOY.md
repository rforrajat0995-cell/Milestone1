# Quick Deployment Checklist

## 🚀 Fast Track Deployment (15 minutes)

### Backend (Render) - 5 minutes

1. ✅ Go to [render.com](https://render.com) → Sign up with GitHub
2. ✅ New → Web Service → Connect GitHub → Select `rforrajat0995-cell/Milestone1`
3. ✅ Configure:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python backend_rag_api.py`
   - Plan: Free
4. ✅ Environment Variables → Add:
   - `GOOGLE_API_KEY=your_key`
   - `PORT=5000`
5. ✅ Create Web Service → Wait for deployment
6. ✅ Copy backend URL (e.g., `https://xxx.onrender.com`)
7. ✅ Initialize data: Render Shell → `python main.py && python build_rag_index.py`

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
3. ✅ Check backend health: `https://xxx.onrender.com/health`

## 🎉 Done!

Your app is live! Every `git push` will auto-deploy.

---

**Full guide**: See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

