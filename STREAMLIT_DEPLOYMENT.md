# Streamlit Cloud Deployment Guide

This guide will help you deploy the Parag Parikh Mutual Funds Assistant to Streamlit Cloud.

## Prerequisites

1. **GitHub Account**: Your code should be pushed to GitHub (already done ✅)
2. **Streamlit Cloud Account**: Sign up at [share.streamlit.io](https://share.streamlit.io)
3. **Groq API Key**: You'll need your Groq API key for the deployment

## Step-by-Step Deployment

### Step 1: Sign in to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "Sign in" and authenticate with your GitHub account
3. Authorize Streamlit Cloud to access your GitHub repositories

### Step 2: Create New App

1. Click the **"New app"** button
2. You'll see a form to configure your app

### Step 3: Configure Your App

Fill in the following details:

- **Repository**: Select `rforrajat0995-cell/Milestone1`
- **Branch**: Select `main`
- **Main file path**: Enter `streamlit_app.py`
- **App URL** (optional): Choose a custom subdomain if desired

### Step 4: Set Up Secrets (Environment Variables)

1. Click **"Advanced settings"** or go to **"Settings"** after creating the app
2. Click on **"Secrets"** tab
3. Add your Groq API key:

```toml
GROQ_API_KEY = "your_groq_api_key_here"
```

**Important**: Replace `your_groq_api_key_here` with your actual Groq API key.

### Step 5: Deploy

1. Click **"Deploy"** or **"Save"**
2. Streamlit Cloud will start building and deploying your app
3. This may take 2-5 minutes on the first deployment

### Step 6: Monitor Deployment

- Watch the deployment logs for any errors
- The app will automatically rebuild when you push changes to the `main` branch
- First deployment may take longer as it needs to:
  - Install dependencies (including sentence-transformers which is large)
  - Build the vector database if needed
  - Initialize the RAG pipeline

## Important Notes

### Vector Database

The vector database (`data/vector_db/mutual_funds.json`) is included in the repository, so it should be available on deployment. However, if it's missing or empty, the app will automatically rebuild it on first load (this may take a few minutes).

### File Size Considerations

- **sentence-transformers**: This package is large (~500MB) and may take time to install
- **Vector database**: The pre-built vector DB is included in the repo
- **Model files**: The embedding model will be downloaded on first use

### Environment Variables

All sensitive data should be stored in Streamlit Secrets:
- `GROQ_API_KEY`: Your Groq API key (required)

### Troubleshooting

**App fails to start:**
- Check the deployment logs for errors
- Verify that `GROQ_API_KEY` is set in Secrets
- Ensure all dependencies are in `requirements.txt`

**Vector DB not found:**
- The app will automatically rebuild it, but this takes time
- Check that `data/storage/funds_database.json` exists in the repo

**Slow first load:**
- This is normal - the app needs to:
  - Download the embedding model (~80MB)
  - Initialize the RAG pipeline
  - Load the vector database

**Out of memory errors:**
- Streamlit Cloud has memory limits
- If you hit limits, consider:
  - Using a smaller embedding model
  - Optimizing the vector database size
  - Using external storage for the vector DB

## Updating Your App

After deployment, any push to the `main` branch will automatically trigger a rebuild and redeploy. You don't need to manually redeploy.

## Accessing Your App

Once deployed, your app will be available at:
```
https://your-app-name.streamlit.app
```

You can find the exact URL in your Streamlit Cloud dashboard.

## Support

If you encounter issues:
1. Check the deployment logs in Streamlit Cloud
2. Review the error messages
3. Ensure all dependencies are correctly specified in `requirements.txt`
4. Verify environment variables are set correctly

