# How to Run the Frontend

## Step 1: Install Frontend Dependencies

```bash
cd frontend
npm install
```

## Step 2: Start the Backend (Terminal 1)

```bash
cd /Users/binoykrishna/Milestone1
source venv/bin/activate
python backend_rag_api.py
```

Wait until you see: `Starting server on http://localhost:5000`

## Step 3: Start the Frontend (Terminal 2)

```bash
cd /Users/binoykrishna/Milestone1/frontend
npm run dev
```

You should see output like:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

## Step 4: Open in Browser

Open your browser and go to: **http://localhost:3000**

## Troubleshooting

### If port 3000 is already in use:
```bash
# Kill the process using port 3000
lsof -ti:3000 | xargs kill -9

# Or use a different port
npm run dev -- --port 3001
```

### If backend connection fails:
- Make sure backend is running on port 5000
- Check: `curl http://localhost:5000/health`
- The frontend will show an error message if backend is not available

### If you see "Cannot find module":
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

