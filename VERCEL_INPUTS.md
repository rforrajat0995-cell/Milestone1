# Vercel Deployment - Exact Inputs

## Step-by-Step Configuration

### 1. Import Project
- Go to [vercel.com](https://vercel.com)
- Click **"Add New..."** → **"Project"**
- Find **`rforrajat0995-cell/Milestone1`**
- Click **"Import"**

---

### 2. Project Settings

#### Framework Preset
```
Other
```
*(or select "Vite" if available)*

#### Root Directory
```
(leave empty - blank)
```

#### Build Command
```
cd frontend && npm install && npm run build
```

#### Output Directory
```
frontend/dist
```

#### Install Command
```
npm install
```
*(default - leave as is)*

---

### 3. Environment Variables (CRITICAL!)

Click **"Environment Variables"** section, then click **"Add"**:

| Field | Value |
|-------|-------|
| **Name** | `GOOGLE_API_KEY` |
| **Value** | `[Your actual Google Gemini API key]` |
| **Environments** | ✅ Production<br>✅ Preview<br>✅ Development<br><br>*(Check ALL THREE boxes)* |

Click **"Save"**

---

### 4. Deploy

Scroll to bottom and click:
```
Deploy
```

---

## Summary - Quick Copy

**Framework Preset:** `Other`  
**Root Directory:** `(empty)`  
**Build Command:** `cd frontend && npm install && npm run build`  
**Output Directory:** `frontend/dist`  
**Install Command:** `npm install` (default)

**Environment Variable:**
- Name: `GOOGLE_API_KEY`
- Value: `[Your API key]`
- Environments: All three (Production, Preview, Development)

---

## After Deployment

Once deployed, test:

1. **Health Check:**
   ```
   https://your-app-name.vercel.app/api/health
   ```

2. **Frontend:**
   ```
   https://your-app-name.vercel.app
   ```

3. **Test Query:**
   Use the frontend to ask: "What is the exit load for Parag Parikh ELSS?"

---

## Notes

- ⚠️ **First request may take 5-10 seconds** (copies data to `/tmp`)
- ✅ **Subsequent requests will be fast**
- ✅ **Auto-deploy:** Every `git push` will redeploy automatically

---

## Troubleshooting

If build fails:
1. Check **Build Logs** in Vercel dashboard
2. Verify **GOOGLE_API_KEY** is set correctly
3. Check that **Output Directory** is exactly `frontend/dist`

