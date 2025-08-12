# Scrptoria

**Scrptoria** is an advanced document intelligence application that transforms static PDF documents into interactive knowledge sources through sophisticated Retrieval-Augmented Generation (RAG) techniques. The application enables users to upload academic papers, textbooks, or technical documents and engage in natural conversations with the content, receiving contextually accurate answers with precise page references.

## 🧠 Advanced RAG Architecture

Scrptoria employs a multi-stage RAG pipeline optimized for academic and technical content:

- **Semantic Chunking**: Documents are intelligently segmented using sentence-aware tokenization that preserves mathematical expressions and maintains semantic coherence across page boundaries
- **Dual-Model Embedding Strategy**: Utilizes BGE-small-en-v1.5 embeddings optimized for speed and accuracy, with careful token management to handle complex academic content
- **Intelligent Reranking**: Implements BGE-reranker-base with dynamic token-aware truncation to identify the most relevant content chunks while maintaining semantic integrity
- **Query Refinement**: Employs context-aware query enhancement using retrieved content to reformulate user questions for better semantic matching
- **Windowed Context Retrieval**: Combines top-ranked chunks with surrounding context windows to provide comprehensive answers while tracking page-level provenance
- **Page-Aware Citation**: Tracks and displays page numbers from only the top 5 most relevant chunks, ensuring citations reflect the highest-confidence sources

The system processes mathematical notation, and technical terminology while maintaining fast response times through optimized batch processing and intelligent caching mechanisms.

## 🚀 Features

- **PDF Upload & Processing**: Upload and process PDF documents with real-time progress
- **AI-Powered Q&A**: Ask questions about uploaded documents using Google's Gemini AI
- **Advanced LaTeX Rendering**: Proper rendering of mathematical expressions and matrices
- **Streaming Responses**: Real-time streaming of AI responses
- **Conversation History**: Maintain context across multiple questions
- **Responsive Design**: Clean, modern interface that works on all devices

## 🏗️ Architecture

- **Frontend**: Next.js with TypeScript, Tailwind CSS, and React
- **Backend**: FastAPI with Python, RAG engine using sentence-transformers and FlagEmbedding
- **AI**: Google Gemini 2.0 Flash for generation, BGE models for embeddings and reranking
- **Vector Storage**: FAISS for efficient similarity search
- **Deployment**: Vercel (frontend) + Railway/Render (backend)

## 📁 Project Structure

```
L2A/
├── frontend/           # Next.js frontend application
│   ├── src/
│   │   ├── components/ # React components (AlternativeLatexRenderer, ErrorBoundary)
│   │   ├── pages/      # Next.js pages (index, _app, _document, debug)
│   │   └── styles/     # CSS styles
│   ├── public/         # Static assets (logo, etc.)
│   ├── package.json
│   ├── next.config.js
│   ├── vercel.json     # Vercel deployment config
│   └── .env.example    # Environment template
├── backend/            # FastAPI backend application
│   ├── app/
│   │   ├── main.py     # FastAPI application
│   │   └── rag.py      # RAG engine implementation
│   ├── bend/           # Virtual environment
│   ├── requirements.txt
│   ├── runtime.txt     # Python version for deployment
│   ├── Procfile        # Railway deployment config
│   ├── start.sh        # Development server script
│   └── .env.example    # Environment template
├── render.yaml         # Render deployment config
├── RAILWAY_DEPLOYMENT.md # Railway deployment guide
└── README.md
```

## 🛠️ Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Google Gemini API key

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv bend
   source bend/bin/activate  # On Windows: bend\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file:
   ```bash
   cp .env.example .env
   # Edit .env and add your GOOGLE_API_KEY
   ```

5. Start the development server:
   ```bash
   ./start.sh
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create environment file:
   ```bash
   cp .env.example .env.local
   # Edit .env.local and set NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

## 🚀 Deployment

### Backend (Railway/Render)
1. Connect your GitHub repository to Railway or Render
2. For Railway: Use the provided `Procfile` and `RAILWAY_DEPLOYMENT.md` guide
3. For Render: Use the `render.yaml` configuration
4. Set environment variables in your deployment platform:
   - `GOOGLE_API_KEY`: Your Google Gemini API key
   - `CORS_ORIGINS`: Your frontend URL (e.g., https://yourapp.vercel.app)

### Frontend (Vercel)
1. Connect your GitHub repository to Vercel
2. Vercel will auto-detect Next.js configuration
3. Set environment variables in Vercel dashboard:
   - `NEXT_PUBLIC_API_BASE_URL`: Your backend URL (e.g., https://yourapp.railway.app)

## 🔧 Environment Variables

### Backend (.env)
```bash
GOOGLE_API_KEY=your_google_gemini_api_key
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## 📚 API Documentation

Once the backend is running, visit:
- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

## 🧪 Key Technologies

### Backend
- **FastAPI**: Modern, fast web framework for Python
- **Sentence Transformers**: BGE-small-en-v1.5 for document embeddings
- **FlagEmbedding**: BGE-reranker-base for intelligent chunk reranking
- **FAISS**: Vector similarity search and indexing
- **Google Gemini 2.0 Flash**: Large language model for Q&A generation
- **PyMuPDF/PyPDF2**: PDF text extraction with fallback support

### Frontend
- **Next.js**: React framework with SSR/SSG
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **React Markdown**: Markdown rendering with LaTeX support
- **KaTeX**: Mathematical notation rendering

## 🔍 Features in Detail

### RAG Engine
- Semantic chunking with sentence-aware tokenization (300 tokens with 20% overlap)
- BGE-small-en-v1.5 embeddings optimized for speed and accuracy
- BGE-reranker-base for intelligent content reranking with token-aware truncation
- FAISS vector indexing for fast similarity search
- Context-aware query refinement using retrieved content
- Windowed context retrieval with page-level provenance tracking
- Smart page citation from top 5 most relevant chunks

### LaTeX Support
- Full mathematical notation rendering
- Matrix and quantum mechanics notation
- Bra-ket notation support
- Custom macro definitions

### Streaming
- Real-time PDF processing progress
- Streaming AI responses
- Live status updates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support, please open an issue on GitHub or check the individual README files in the `frontend/` and `backend/` directories for more detailed setup instructions.