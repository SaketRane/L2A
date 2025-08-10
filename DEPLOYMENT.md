# Deployment Checklist

## Pre-deployment Setup

### 1. Environment Variables
- [ ] Get Google Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- [ ] Backend `.env` file created (for local development)
- [ ] Frontend `.env.local` file created (for local development)

### 2. GitHub Repository
- [ ] Code pushed to GitHub repository
- [ ] Repository is public or accessible to deployment services
- [ ] All sensitive files (.env, .env.local) are in .gitignore

## Backend Deployment (Render)

### Setup
- [ ] Connect GitHub repository to Render
- [ ] Select "Web Service" deployment type
- [ ] Use the `render.yaml` configuration (automatic detection)

### Environment Variables (Set in Render Dashboard)
- [ ] `GOOGLE_API_KEY`: Your Google Gemini API key
- [ ] `ENVIRONMENT`: `production`
- [ ] `CORS_ORIGINS`: Your frontend domain (will be set after frontend deployment)

### Post-deployment
- [ ] Note your backend URL (e.g., `https://your-app.onrender.com`)
- [ ] Test health endpoint: `https://your-app.onrender.com/health`

## Frontend Deployment (Vercel)

### Setup
- [ ] Connect GitHub repository to Vercel
- [ ] Vercel auto-detects Next.js configuration
- [ ] Use automatic build settings

### Environment Variables (Set in Vercel Dashboard)
- [ ] `NEXT_PUBLIC_API_BASE_URL`: Your backend URL from Render

### Post-deployment
- [ ] Note your frontend URL (e.g., `https://your-app.vercel.app`)
- [ ] Update backend's `CORS_ORIGINS` with this URL

## Final Configuration

### Update Backend CORS
- [ ] Go to Render dashboard → Your service → Environment
- [ ] Update `CORS_ORIGINS` to include your Vercel URL:
  ```
  CORS_ORIGINS=https://your-app.vercel.app
  ```
- [ ] Redeploy backend service

### Testing
- [ ] Frontend loads correctly
- [ ] Can upload PDF files
- [ ] Can ask questions and get responses
- [ ] LaTeX rendering works properly
- [ ] No CORS errors in browser console

## Troubleshooting

### Common Issues
1. **CORS Errors**: Make sure backend `CORS_ORIGINS` includes your frontend URL
2. **API Connection Failed**: Verify `NEXT_PUBLIC_API_BASE_URL` is correct
3. **Build Failures**: Check logs in deployment dashboard
4. **Environment Variables**: Ensure all required variables are set

### Useful Commands
```bash
# Test backend locally
cd backend
./start.sh

# Test frontend locally  
cd frontend
npm run dev

# Build frontend for production
npm run build
npm start
```

## Development Workflow

### Making Changes
1. Make changes locally
2. Test thoroughly
3. Commit and push to GitHub
4. Deployments will trigger automatically

### Adding Features
1. Create feature branch
2. Develop and test locally
3. Create pull request
4. Merge to main
5. Auto-deploy to production
