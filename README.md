# L2A - AI-Powered PDF Q&A System

A full-stack application that allows users to upload PDF documents and ask questions about their content using AI-powered RAG (Retrieval-Augmented Generation) technology.

## 🚀 Features

- **PDF Upload & Processing**: Upload and process PDF documents with real-time progress
- **AI-Powered Q&A**: Ask questions about uploaded documents using Google's Gemini AI
- **Advanced LaTeX Rendering**: Proper rendering of mathematical expressions and matrices
- **Streaming Responses**: Real-time streaming of AI responses
- **Conversation History**: Maintain context across multiple questions
- **Responsive Design**: Clean, modern interface that works on all devices

## 🏗️ Architecture

- **Frontend**: Next.js with TypeScript, Tailwind CSS, and React
- **Backend**: FastAPI with Python, RAG engine using sentence-transformers
- **AI**: Google Gemini API for generation, BGE models for embeddings
- **Deployment**: Vercel (frontend) + Render (backend)

## 📁 Project Structure

```
L2A/
├── frontend/           # Next.js frontend application
│   ├── src/
│   │   ├── components/ # React components
│   │   ├── pages/      # Next.js pages
│   │   └── styles/     # CSS styles
│   ├── package.json
│   ├── next.config.js
│   └── vercel.json     # Vercel deployment config
├── backend/            # FastAPI backend application
│   ├── app/
│   │   ├── main.py     # FastAPI application
│   │   └── rag.py      # RAG engine implementation
│   ├── requirements.txt
│   ├── start.sh        # Development server script
│   └── start_production.sh # Production server script
├── render.yaml         # Render deployment config
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

### Backend (Render)
1. Connect your GitHub repository to Render
2. Render will detect the `render.yaml` configuration automatically
3. Set environment variables in Render dashboard:
   - `GOOGLE_API_KEY`: Your Google Gemini API key
   - `CORS_ORIGINS`: Your frontend URL

### Frontend (Vercel)
1. Connect your GitHub repository to Vercel
2. Vercel will auto-detect Next.js configuration
3. Set environment variables in Vercel dashboard:
   - `NEXT_PUBLIC_API_BASE_URL`: Your backend URL from Render

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
- **Sentence Transformers**: For document embeddings
- **FAISS**: Vector similarity search
- **Google Gemini**: Large language model for Q&A
- **PyMuPDF**: PDF text extraction

### Frontend
- **Next.js**: React framework with SSR/SSG
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **React Markdown**: Markdown rendering with LaTeX support
- **KaTeX**: Mathematical notation rendering

## 🔍 Features in Detail

### RAG Engine
- Chunked document processing with overlap
- BGE-large embeddings for semantic search
- FAISS vector indexing for fast retrieval
- Context-aware response generation

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