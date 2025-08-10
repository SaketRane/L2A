# L2A Backend Deployment Guide

## Render Deployment

### Option 1: Using render.yaml (Recommended)
1. Connect your GitHub repository to Render
2. Render will automatically detect the `render.yaml` file
3. Set the `GOOGLE_API_KEY` environment variable in the Render dashboard
4. Update `CORS_ORIGINS` in render.yaml with your frontend URL

### Option 2: Manual Setup
1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set the following:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `./start.sh production`
   - **Environment Variables**:
     - `GOOGLE_API_KEY`: Your Google API key
     - `ENVIRONMENT`: `production`
     - `CORS_ORIGINS`: Your frontend URL (e.g., `https://myapp.vercel.app`)

### Environment Variables Required
- `GOOGLE_API_KEY`: Your Google Generative AI API key
- `ENVIRONMENT`: Set to `production`
- `CORS_ORIGINS`: Comma-separated list of allowed origins

### Health Check
The service includes a health check endpoint at `/health` that Render will use to monitor the service.

### Local Development
Use `./start.sh` for local development with hot reload.
Use `./start.sh production` to test production configuration locally.

## Files Structure for Deployment
```
backend/
├── app/
│   ├── main.py
│   ├── rag.py
│   └── __init__.py
├── requirements.txt
├── start.sh (unified development/production)
└── .env (local only, not deployed)
```

## Notes
- The virtual environment (`bend/`) is not needed for deployment
- Render will install dependencies automatically
- Environment variables should be set in Render dashboard, not in code
- The service will create necessary directories (`uploads/`, `data/`, `logs/`) on startup
