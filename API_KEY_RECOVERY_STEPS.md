# API Key Recovery Steps

Since your API key was exposed and revoked, follow these steps to get back up and running:

## ✅ Step 1: Generate a New API Key

1. Go to **[Google AI Studio](https://aistudio.google.com/app/apikey)**
2. Sign in with your Google account
3. Click **"Create API Key"** or **"Get API Key"**
4. If prompted, create a new Google Cloud project (or select existing)
5. **Copy the new API key immediately** (you won't see it again)

## ✅ Step 2: Update Local .env File

1. Open your `.env` file in the project root:
   ```bash
   cd /Users/binoykrishna/Milestone1
   nano .env
   # or use your preferred editor
   ```

2. Update the API key:
   ```
   GOOGLE_API_KEY=your_new_api_key_here
   ```

3. Save the file

4. Verify it's set:
   ```bash
   python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key:', os.getenv('GOOGLE_API_KEY')[:10] + '...' if os.getenv('GOOGLE_API_KEY') else 'Not found')"
   ```

## ✅ Step 3: Update Vercel Environment Variables

1. Go to **[Vercel Dashboard](https://vercel.com/dashboard)**
2. Select your project: `Milestone1`
3. Go to **Settings** → **Environment Variables**
4. Find `GOOGLE_API_KEY`
5. Click **Edit** (or delete and recreate)
6. Paste your **new API key**
7. Make sure all environments are checked:
   - ✅ Production
   - ✅ Preview
   - ✅ Development
8. Click **Save**

## ✅ Step 4: Test Locally

Test that the new key works:

```bash
cd /Users/binoykrishna/Milestone1
source venv/bin/activate
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')
if api_key:
    print('✓ API key found')
    # Test with a simple API call
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    print('✓ API key is valid')
else:
    print('✗ API key not found')
"
```

## ✅ Step 5: Redeploy on Vercel (if needed)

If your Vercel deployment was using the old key:

1. Go to Vercel Dashboard
2. Click on your project
3. Go to **Deployments** tab
4. Click **"Redeploy"** on the latest deployment
   - Or just push a new commit to trigger auto-deploy

## ✅ Step 6: Resolve GitHub Security Alert

1. Go to your GitHub repository
2. Click on the **Security** tab
3. Find the **"Secrets detected"** alert
4. Click on it
5. Mark as **"Resolved"** or **"False positive"** (since you've revoked the key)

## 🔒 Security Best Practices

Going forward:

- ✅ **Never commit real API keys** to Git
- ✅ **Use placeholders** in documentation (e.g., `AIzaSy...example`)
- ✅ **Always use `.env` files** for real keys (already in `.gitignore`)
- ✅ **If a key is exposed, revoke it immediately** (you did this! ✅)
- ✅ **Rotate keys periodically** for security

## 🎉 You're Done!

After completing these steps:
- ✅ New API key generated
- ✅ Local `.env` updated
- ✅ Vercel environment variables updated
- ✅ GitHub security alert resolved
- ✅ Everything should work again!

