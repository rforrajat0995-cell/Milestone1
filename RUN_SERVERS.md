# Step-by-Step Guide: Running the Frontend and Backend Servers

## Prerequisites Check

Before starting, make sure you have:
- ✅ Python virtual environment activated
- ✅ All Python dependencies installed (`pip install -r requirements.txt`)
- ✅ Node.js and npm installed (check with `node --version` and `npm --version`)
- ✅ Frontend dependencies installed (`cd frontend && npm install`)

---

## Step 1: Open Terminal 1 (Backend Server)

### 1.1 Navigate to Project Directory
```bash
cd /Users/binoykrishna/Milestone1
```

### 1.2 Activate Virtual Environment
```bash
source venv/bin/activate
```

You should see `(venv)` appear at the beginning of your terminal prompt.

### 1.3 Verify You're in the Right Directory
```bash
pwd
```
Should show: `/Users/binoykrishna/Milestone1`

### 1.4 Start the Backend Server
```bash
python backend_rag_api.py
```

### 1.5 Expected Output
You should see something like:
```
======================================================================
Mutual Fund FAQ Assistant - RAG Backend API
======================================================================

Starting server on http://localhost:5000

Endpoints:
  POST /query - Answer queries about mutual funds (RAG)
  GET  /funds - List all available funds
  GET  /health - Health check

======================================================================

 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

**✅ Keep this terminal window open!** The backend server is now running.

---

## Step 2: Open Terminal 2 (Frontend Server)

**Open a NEW terminal window** (don't close Terminal 1!)

### 2.1 Navigate to Frontend Directory
```bash
cd /Users/binoykrishna/Milestone1/frontend
```

### 2.2 Verify You're in the Frontend Directory
```bash
pwd
```
Should show: `/Users/binoykrishna/Milestone1/frontend`

### 2.3 Check if Dependencies are Installed
```bash
ls node_modules
```
If you see a list of folders, dependencies are installed. If not, run:
```bash
npm install
```

### 2.4 Start the Frontend Development Server
```bash
npm run dev
```

### 2.5 Expected Output
You should see something like:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

**✅ Keep this terminal window open too!** The frontend server is now running.

---

## Step 3: Open Your Browser

### 3.1 Open Your Web Browser
Open Chrome, Firefox, Safari, or any modern browser.

### 3.2 Navigate to the Frontend
Type in the address bar:
```
http://localhost:3000
```

Or simply click on the link shown in Terminal 2: `http://localhost:3000/`

### 3.3 What You Should See
- A dark-themed chat interface
- Left sidebar with "My Chats"
- Main area with welcome message: "How can I help you today?"
- Input box at the bottom

---

## Step 4: Test the Application

### 4.1 Test Backend Health (Optional)
In a new terminal, you can verify the backend is running:
```bash
curl http://localhost:5000/health
```

Should return:
```json
{"status":"healthy","service":"Mutual Fund FAQ Assistant (RAG)","rag_ready":true}
```

### 4.2 Test Frontend Connection
1. Type a question in the chat input box, for example:
   ```
   What is the exit load for ELSS?
   ```

2. Press Enter or click the send button (green arrow)

3. You should see:
   - Your question appear on the right side
   - A loading indicator
   - An answer from the assistant
   - A source URL link

---

## Troubleshooting

### Problem: "Port 5000 already in use"
**Solution:**
```bash
# Find what's using port 5000
lsof -i :5000

# Kill the process (replace PID with the number from above)
kill -9 <PID>
```

### Problem: "Port 3000 already in use"
**Solution:**
```bash
# Find what's using port 3000
lsof -i :3000

# Kill the process
kill -9 <PID>

# Or use a different port
npm run dev -- --port 3001
```

### Problem: "Cannot find module" in frontend
**Solution:**
```bash
cd /Users/binoykrishna/Milestone1/frontend
rm -rf node_modules package-lock.json
npm install
```

### Problem: "RAG pipeline not initialized" in backend
**Solution:**
- Make sure your `.env` file has `GOOGLE_API_KEY` set
- Or the system will use local embeddings (which is fine)

### Problem: Frontend shows "error processing your query"
**Solution:**
- Check if backend is running (Terminal 1)
- Check backend logs for errors
- Verify: `curl http://localhost:5000/health`

---

## Quick Reference: What Should Be Running

When everything is working, you should have:

1. **Terminal 1:** Backend server running on `http://localhost:5000`
   - Shows Flask debug output
   - Processes API requests

2. **Terminal 2:** Frontend server running on `http://localhost:3000`
   - Shows Vite dev server output
   - Serves the React app

3. **Browser:** Open to `http://localhost:3000`
   - Shows the chat interface
   - Can send queries and receive answers

---

## Stopping the Servers

### To Stop Backend (Terminal 1):
Press `Ctrl + C` in Terminal 1

### To Stop Frontend (Terminal 2):
Press `Ctrl + C` in Terminal 2

---

## Summary Checklist

- [ ] Terminal 1: Backend running on port 5000
- [ ] Terminal 2: Frontend running on port 3000
- [ ] Browser: Open to http://localhost:3000
- [ ] Can send a test query
- [ ] Receives answer with source URL

If all checkboxes are checked, you're all set! 🎉

