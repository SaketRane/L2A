# Railway Deployment Guide for L2A Backend

## 🚂 Quick Railway Deployment

### Option 1: One-Click Deploy (Recommended)
1. Go to [Railway](https://railway.app)
2. Click **"Start a New Project"**
3. Select **"Deploy from GitHub repo"**
4. Connect your GitHub account and select **"L2A"** repository
5. Railway will auto-detect the backend and start deployment

### Option 2: Railway CLI
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
cd backend
railway init

# Deploy
railway up
```

### Environment Variables (Set in Railway Dashboard)
After deployment starts, set these environment variables:

1. **GOOGLE_API_KEY**: `AIzaSyDjiuP36smPH78MOHoqpu7b`
2. **ENVIRONMENT**: `production`
3. **CORS_ORIGINS**: `https://your-frontend-domain.com` (update after frontend deployment)

### Railway Configuration
- **Build Command**: `pip install -r requirements.txt` (auto-detected)
- **Start Command**: `./start.sh production` (configured in Procfile)
- **Runtime**: Python 3.11 (specified in runtime.txt)
- **Health Check**: `/health` endpoint
- **Port**: Automatically assigned by Railway (handled by $PORT)

### Expected Resource Usage
- **Memory**: ~2GB (for AI models)
- **CPU**: Medium usage during model loading, low during idle
- **Storage**: ~1GB for dependencies and models

### Testing Your Deployment
Once deployed, you'll get a URL like: `https://l2a-backend-production.up.railway.app`

Test endpoints:
- Health: `https://your-url/health`
- API Docs: `https://your-url/docs`

### Railway Free Tier
- **$5 credit per month** (usually sufficient for development/testing)
- **No sleep/spin-down** (unlike other free tiers)
- **Up to 8GB RAM** available
- **Pay-per-usage** after credits

### Troubleshooting
- **Build fails**: Check build logs in Railway dashboard
- **Memory issues**: Railway auto-scales, but monitor usage
- **Startup slow**: AI models take 1-2 minutes to load initially
- **Environment variables**: Make sure all required vars are set

### Advantages over Render
- ✅ Better free tier ($5 credit vs limited free)
- ✅ No sleep/spin-down on free tier  
- ✅ More generous resource limits
- ✅ Faster deployment process
- ✅ Better suited for AI/ML applications

### Next Steps
1. Deploy backend on Railway
2. Note your Railway backend URL
3. Deploy frontend on Vercel
4. Update CORS_ORIGINS with frontend URL
