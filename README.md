# Mutual Fund FAQ Assistant

A RAG (Retrieval Augmented Generation) based chatbot that answers factual questions about mutual fund schemes using official public data from Groww. The system provides accurate information about expense ratios, exit loads, minimum SIP amounts, lock-in periods, riskometers, and benchmarks.

## 🚀 Features

- **RAG-Based Q&A**: Uses Google Gemini for embeddings and LLM generation
- **Factual Information Only**: Answers questions about mutual fund schemes without providing investment advice
- **Source URLs**: Every answer includes source links from official Groww pages
- **Pre-computed Data**: Data is scraped and stored locally for fast retrieval
- **Modern UI**: Clean React frontend with chat interface
- **Vector Search**: ChromaDB for efficient semantic search
- **Local Fallback**: Uses sentence-transformers for embeddings if Gemini API quota is exceeded

## 🛠️ Tech Stack

### Backend
- **Python 3.8+**
- **Flask**: REST API server
- **Google Gemini API**: Embeddings (`models/embedding-001`) and LLM (`models/gemini-2.0-flash`)
- **ChromaDB**: Vector database for semantic search
- **BeautifulSoup**: Web scraping
- **sentence-transformers**: Local embedding fallback

### Frontend
- **React 18**
- **Vite**: Build tool and dev server
- **Modern CSS**: Responsive design

## 📋 Prerequisites

- Python 3.8 or higher
- Node.js 16+ and npm
- Google Gemini API key ([Get one here](https://aistudio.google.com/app/apikey))
- Git (for cloning)

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd Milestone1
```

### 2. Backend Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your Google Gemini API key:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

### 4. Frontend Setup

```bash
cd frontend
npm install
```

Create `frontend/.env` file:

```bash
cp .env.example .env
```

Edit `frontend/.env` (optional, defaults to localhost):

```env
VITE_API_BASE_URL=http://localhost:5000
```

### 5. Initialize Data

First, scrape the mutual fund data:

```bash
# Make sure virtual environment is activated
python main.py
```

Then, build the RAG index:

```bash
python build_rag_index.py
```

## 🏃 Running Locally

### Start Backend Server

```bash
# Activate virtual environment
source venv/bin/activate

# Start Flask server
python backend_rag_api.py
```

The backend will start on `http://localhost:5000`

### Start Frontend Server

Open a new terminal:

```bash
cd frontend
npm run dev
```

The frontend will start on `http://localhost:3000`

### Access the Application

Open your browser and navigate to: **http://localhost:3000**

## 📁 Project Structure

```
Milestone1/
├── backend_rag_api.py      # Flask REST API server
├── scraper.py              # Web scraper for Groww pages
├── rag_pipeline.py         # RAG system orchestration
├── data_chunking.py        # Text chunking for RAG
├── embeddings.py           # Google Gemini embeddings
├── embeddings_local.py     # Local embedding fallback
├── vector_store.py         # ChromaDB integration
├── data_storage.py         # JSON data storage
├── config.py               # Scraper configuration
├── config_rag.py           # RAG configuration
├── validators.py           # Data validation
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── data/
│   ├── storage/
│   │   └── funds_database.json  # Scraped fund data
│   └── vector_db/          # ChromaDB vector database
└── frontend/
    ├── src/
    │   ├── App.jsx         # Main React component
    │   ├── App.css         # Styles
    │   └── main.jsx        # Entry point
    ├── package.json        # Node dependencies
    ├── vite.config.js      # Vite configuration
    └── .env.example        # Frontend env template
```

## 🔌 API Endpoints

### Health Check
```
GET /health
```
Returns server status and RAG pipeline readiness.

### Query
```
POST /query
Content-Type: application/json

{
  "query": "What's the exit load of Parag Parikh Arbitrage Fund Direct Growth?"
}
```

Response:
```json
{
  "success": true,
  "answer": "The exit load for Parag Parikh Arbitrage Fund Direct Growth is 0.25%, if redeemed within 30 days.",
  "source_urls": ["https://groww.in/mutual-funds/parag-parikh-arbitrage-fund-direct-growth"],
  "query": "What's the exit load of Parag Parikh Arbitrage Fund Direct Growth?",
  "retrieved_chunks": 3
}
```

### List Funds
```
GET /funds
```
Returns list of all available funds in the database.

## 🚢 Deployment

### Backend Deployment (Railway)

1. **Sign up at [Railway.app](https://railway.app)**
2. **Create New Project** → Deploy from GitHub
3. **Select your repository**
4. **Add Environment Variables:**
   - `GOOGLE_API_KEY`: Your Google Gemini API key
5. **Railway will auto-detect Python** and install dependencies
6. **Set Start Command:** `python backend_rag_api.py`
7. **Note the backend URL** (e.g., `https://your-app.railway.app`)

### Frontend Deployment (Vercel)

1. **Sign up at [Vercel.com](https://vercel.com)**
2. **Import project** from GitHub
3. **Configure Build Settings:**
   - Framework Preset: Vite
   - Build Command: `cd frontend && npm install && npm run build`
   - Output Directory: `frontend/dist`
4. **Add Environment Variable:**
   - `VITE_API_BASE_URL`: Your Railway backend URL
5. **Deploy**

### Data Initialization on Deployment

Since `data/vector_db/` is not in Git, you need to initialize it on the server:

**Option 1: Run on Railway (Recommended)**
- Add a startup script that runs `python main.py` and `python build_rag_index.py` on first deploy
- Or use Railway's one-off commands

**Option 2: Pre-build and Upload**
- Build the vector DB locally
- Upload `data/vector_db/` and `data/storage/funds_database.json` to Railway

## 🔒 Security

- ✅ No hardcoded API keys (all use environment variables)
- ✅ `.env` files are gitignored
- ✅ Sensitive data excluded from repository
- ✅ CORS configured for production

## 📝 Configuration

### Adding More Funds

Edit `config.py` to add more mutual funds:

```python
PARAG_PARIKH_FUNDS = {
    "Fund Name": "url-slug",
    # Add more funds here
}
```

Then re-scrape:
```bash
python main.py
python build_rag_index.py
```

### RAG Configuration

Edit `config_rag.py` to adjust:
- Chunk size and overlap
- Number of retrieved chunks (TOP_K_RETRIEVAL)
- LLM temperature
- Max tokens

## 🧪 Testing

### Test the Scraper
```bash
python test_scraper.py
```

### Test the RAG System
```bash
python test_rag.py
```

### Test Backend API
```bash
curl http://localhost:5000/health
```

## 🐛 Troubleshooting

### Backend Issues

**"No Google API key found"**
- Check `.env` file exists and has `GOOGLE_API_KEY`
- Verify API key is valid at [Google AI Studio](https://aistudio.google.com/app/apikey)

**"429 Quota Exceeded"**
- The system will automatically fallback to local embeddings
- Consider upgrading your Gemini API plan

**"Vector DB not found"**
- Run `python build_rag_index.py` to create the index

### Frontend Issues

**"Backend not connected"**
- Ensure backend is running on port 5000
- Check `VITE_API_BASE_URL` in `frontend/.env`
- Check CORS settings in `backend_rag_api.py`

**"Cannot find module"**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## 📚 Documentation

- [RAG System Details](RAG_README.md)
- [Gemini API Setup](SETUP_GEMINI.md)
- [Running Servers Guide](RUN_SERVERS.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is for educational purposes. Please ensure compliance with Groww's terms of service when scraping their website.

## ⚠️ Disclaimer

This assistant provides **factual information only** and does **NOT** provide investment advice. All information is sourced from public Groww pages. Users should consult with financial advisors before making investment decisions.

## 🙏 Acknowledgments

- Data sourced from [Groww.in](https://groww.in)
- Powered by Google Gemini API
- Built with Flask, React, and ChromaDB

---

**Note**: This is a facts-only assistant. It does not provide investment advice or recommendations.
