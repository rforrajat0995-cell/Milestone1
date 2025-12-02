# Setup Guide: Google Gemini API Key

## Step 1: Get Your Google Gemini API Key

1. **Visit Google AI Studio:**
   - Go to: https://aistudio.google.com/app/apikey

2. **Sign in:**
   - Use your Google account to sign in

3. **Create API Key:**
   - Click on "Get API key" or "Create API key"
   - If prompted, create a new Google Cloud project (or select existing)
   - Your API key will be generated

4. **Copy the API Key:**
   - The API key will look like: `AIzaSy...` (starts with "AIza")
   - Copy it immediately (you won't be able to see it again)

## Step 2: Add API Key to Your Project

### Option A: Using .env file (Recommended)

1. **Create `.env` file in project root:**
   ```bash
   cd /Users/binoykrishna/Milestone1
   touch .env
   ```

2. **Add your API key:**
   ```bash
   echo "GOOGLE_API_KEY=AIzaSy_your_actual_key_here" > .env
   ```
   
   Or edit `.env` file manually:
   ```
   GOOGLE_API_KEY=AIzaSy_your_actual_key_here
   ```

3. **Verify the file:**
   ```bash
   cat .env
   ```

### Option B: Using Environment Variable

```bash
export GOOGLE_API_KEY=AIzaSy_your_actual_key_here
```

**Note:** This only works for the current terminal session. For permanent setup, use `.env` file.

## Step 3: Install Dependencies

```bash
source venv/bin/activate
pip install -r requirements.txt
```

This will install:
- `google-generativeai` - Google Gemini SDK
- `chromadb` - Vector database
- `python-dotenv` - For loading .env file

## Step 4: Verify Setup

Test that your API key works:

```bash
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')
if api_key:
    print('✓ API key found:', api_key[:10] + '...')
else:
    print('✗ API key not found')
"
```

## Step 5: Build RAG Index

Once API key is set, build the vector index:

```bash
python build_rag_index.py
```

## Step 6: Test RAG System

```bash
python test_rag.py
```

## Troubleshooting

### Error: "API key not found"
- Check `.env` file exists in project root
- Verify `GOOGLE_API_KEY=...` is in the file (no spaces around `=`)
- Make sure you're running from the project directory

### Error: "Invalid API key"
- Verify you copied the complete API key
- Check if API key has expired (regenerate if needed)
- Ensure you're using Gemini API key, not other Google Cloud keys

### Error: "Quota exceeded"
- Free tier has rate limits
- Wait a few minutes and try again
- Check usage at: https://aistudio.google.com/app/apikey

## Security Notes

⚠️ **Important:**
- Never commit `.env` file to git (it's already in `.gitignore`)
- Don't share your API key publicly
- Regenerate key if accidentally exposed

## Cost Information

Google Gemini offers a **free tier** with generous limits:
- **Free tier**: 15 requests per minute, 1500 requests per day
- **Paid tier**: Higher limits available

For this project, the free tier should be sufficient for development and testing.

## Next Steps

After setting up the API key:
1. ✅ Run `python data_storage.py` (if not done) - Collect fund data
2. ✅ Run `python build_rag_index.py` - Build vector index
3. ✅ Run `python test_rag.py` - Test the RAG system

