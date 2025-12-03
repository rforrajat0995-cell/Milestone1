# Step-by-Step: Test Your Backend

Complete guide to test your deployed backend on Render.

## 📍 Where to Run Commands

**All commands go in Terminal (Mac)**

1. **Open Terminal:**
   - Press `Cmd + Space` (Spotlight)
   - Type "Terminal"
   - Press Enter
   - OR: Applications → Utilities → Terminal

2. **You're ready!** Terminal is where you'll run all the commands below.

---

## 🧪 Step 1: Initialize Backend Data

This will scrape the mutual fund data and build the RAG index.

### Command:
```bash
curl -X POST https://milestone1-c4yb.onrender.com/init
```

### Where to run:
- Open Terminal (see above)
- Copy the command above
- Paste it in Terminal (Cmd + V)
- Press Enter

### What to expect:
- **First 30-60 seconds**: Service waking up (free tier spin-up)
- **Next 2-3 minutes**: Scraping data (you'll see progress)
- **Next 1-2 minutes**: Building RAG index
- **Total time**: 5-10 minutes

### Success looks like:
```json
{
  "success": true,
  "message": "Data initialized successfully",
  "scraper_output": "...",
  "index_output": "..."
}
```

### If you see errors:
- Wait and try again (service might be spinning up)
- Check Render logs for details
- Common: Timeout errors - just retry

**⏱️ Wait for this to complete before moving to Step 2!**

---

## ✅ Step 2: Test Health Endpoint

Verify the backend is running and healthy.

### Command:
```bash
curl https://milestone1-c4yb.onrender.com/health
```

### Where to run:
- Same Terminal window
- Copy and paste the command
- Press Enter

### Success looks like:
```json
{
  "status": "healthy",
  "service": "Mutual Fund FAQ Assistant (RAG)",
  "rag_ready": true,
  "message": "Service is running. RAG pipeline may need data initialization."
}
```

**Note**: `rag_ready` should be `true` after Step 1 completes.

---

## 📋 Step 3: List Available Funds

Check if funds data was loaded correctly.

### Command:
```bash
curl https://milestone1-c4yb.onrender.com/funds
```

### Where to run:
- Same Terminal window
- Copy and paste
- Press Enter

### Success looks like:
```json
{
  "success": true,
  "count": 7,
  "funds": [
    {
      "fund_name": "Parag Parikh ELSS Tax Saver Fund Direct Growth",
      "source_url": "https://groww.in/mutual-funds/..."
    },
    ...
  ]
}
```

**Expected**: Should show 7 funds (all Parag Parikh funds).

---

## 🔍 Step 4: Test Query Endpoint

Test the RAG system with a real query.

### Command:
```bash
curl -X POST https://milestone1-c4yb.onrender.com/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the exit load for Parag Parikh ELSS?"}'
```

### Where to run:
- Same Terminal window
- Copy the ENTIRE command (all 3 lines)
- Paste in Terminal
- Press Enter

**Important**: The backslash `\` means the command continues on the next line. Make sure you copy all 3 lines!

### Success looks like:
```json
{
  "success": true,
  "answer": "The exit load for Parag Parikh ELSS Tax Saver Fund Direct Growth is Nil.",
  "source_urls": [
    "https://groww.in/mutual-funds/parag-parikh-elss-tax-saver-fund-direct-growth"
  ],
  "query": "What is the exit load for Parag Parikh ELSS?",
  "retrieved_chunks": 3
}
```

---

## 🧪 Step 5: Test More Queries

Try different questions to verify everything works.

### Test 1: Expense Ratio
```bash
curl -X POST https://milestone1-c4yb.onrender.com/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the expense ratio of Parag Parikh Arbitrage Fund?"}'
```

### Test 2: Riskometer
```bash
curl -X POST https://milestone1-c4yb.onrender.com/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the risk factor for Parag Parikh Conservative Hybrid Fund?"}'
```

### Test 3: Multiple Fields
```bash
curl -X POST https://milestone1-c4yb.onrender.com/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Tell me about Parag Parikh Liquid Fund - expense ratio and exit load"}'
```

---

## 📊 Expected Results Summary

| Endpoint | Expected Result |
|----------|----------------|
| `/health` | `"status": "healthy"`, `"rag_ready": true` |
| `/funds` | 7 funds listed |
| `/query` | Answer with source URL |

---

## 🐛 Troubleshooting

### Issue: "Connection refused" or timeout
**Solution**: 
- Wait 30-60 seconds (free tier spin-up)
- Try again
- Check Render dashboard - service should be "Live"

### Issue: `/init` times out
**Solution**:
- This is normal - it takes 5-10 minutes
- Check Render logs to see progress
- If it fails, try again

### Issue: `rag_ready: false` after initialization
**Solution**:
- Check Render logs for errors
- Verify data files exist
- Try `/init` again

### Issue: Query returns "RAG pipeline not initialized"
**Solution**:
- Make sure Step 1 (`/init`) completed successfully
- Check `/health` - `rag_ready` should be `true`
- If not, run `/init` again

---

## ✅ Success Checklist

After testing, you should have:
- [ ] `/init` completed successfully
- [ ] `/health` shows `rag_ready: true`
- [ ] `/funds` lists 7 funds
- [ ] `/query` returns answers with source URLs
- [ ] Multiple queries work correctly

---

## 🎯 Next Steps

Once all tests pass:
1. ✅ Backend is fully functional
2. ✅ Ready to deploy frontend
3. ✅ You have the backend URL: `https://milestone1-c4yb.onrender.com`

**Proceed to frontend deployment!** 🚀

