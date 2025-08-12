# Scrptoria Backend

**Scrptoria Backend** is a FastAPI-based service that powers the advanced RAG (Retrieval-Augmented Generation) engine for document intelligence and conversational Q&A.

## 🚀 Deployment

### Railway Deployment (Recommended)
1. Connect your GitHub repository to Railway
2. Railway will automatically detect the `Procfile` and Python runtime
3. Set environment variables in Railway dashboard:
   - `GOOGLE_API_KEY`: Your Google Gemini API key
   - `CORS_ORIGINS`: Your frontend URL (e.g., `https://scrptoria.vercel.app`)

### Render Deployment (Alternative)
### Render Deployment (Alternative)
1. Connect your GitHub repository to Render
2. Render will automatically detect the `render.yaml` file
3. Set the `GOOGLE_API_KEY` environment variable in the Render dashboard
4. Update `CORS_ORIGINS` in render.yaml with your frontend URL

### Manual Setup
1. Create a new Web Service on Railway or Render
2. Connect your GitHub repository
3. Set the following:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `./start.sh production` (or see Procfile for Railway)
   - **Environment Variables**:
     - `GOOGLE_API_KEY`: Your Google API key
     - `ENVIRONMENT`: `production`
     - `CORS_ORIGINS`: Your frontend URL (e.g., `https://scrptoria.vercel.app`)

## 🔧 Environment Variables Required
- `GOOGLE_API_KEY`: Your Google Generative AI API key for Gemini 2.0 Flash
- `ENVIRONMENT`: Set to `production` for deployment, `development` for local
- `CORS_ORIGINS`: Comma-separated list of allowed origins

## 🏥 Health Check
The service includes a health check endpoint at `/health` that deployment platforms will use to monitor the service.

## 🛠️ Local Development
```bash
# Copy environment template
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# Install dependencies
pip install -r requirements.txt

# Start development server
./start.sh
```

Use `./start.sh` for local development with hot reload.
Use `./start.sh production` to test production configuration locally.

## 📁 Files Structure for Deployment
```
backend/
├── app/
│   ├── main.py         # FastAPI application
│   ├── rag.py          # RAG engine with BGE models
│   └── __init__.py
├── requirements.txt    # Python dependencies
├── runtime.txt         # Python version specification
├── Procfile           # Railway deployment configuration
├── start.sh           # Development/production startup script
├── .env.example       # Environment template
└── .railwayignore     # Files to ignore in Railway deployment
```

## 🧠 RAG Engine Features
- **BGE-small-en-v1.5** embeddings for fast, accurate semantic search
- **BGE-reranker-base** for intelligent content reranking
- **FAISS** vector indexing for efficient similarity search
- **Semantic chunking** with sentence-aware tokenization
- **Query refinement** using context-aware enhancement
- **Page-level citation** tracking from top relevant chunks
- **Windowed context retrieval** the top context chunks are passed to the LLM along with a window of other chunks around them

## 📚 API Documentation
Once the backend is running, visit:
- **API Docs**: `https://your-backend-url.railway.app/docs`
- **Health Check**: `https://your-backend-url.railway.app/health`

## 📝 Notes
- The virtual environment (`bend/`) is not needed for deployment
- Railway/Render will install dependencies automatically
- Environment variables should be set in dashboard, not in code
- The service will create necessary directories (`uploads/`, `data/`, `logs/`) on startup
- PDF processing creates local FAISS indexes and chunk files for caching
