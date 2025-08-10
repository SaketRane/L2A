# L2A Frontend Deployment Guide

## Vercel Deployment

### Option 1: Automatic Deployment (Recommended)
1. Push your code to GitHub
2. Connect your GitHub repository to Vercel
3. Vercel will automatically detect Next.js and configure build settings
4. Set environment variables in Vercel dashboard

### Option 2: Using Vercel CLI
```bash
npm install -g vercel
vercel
```

### Environment Variables Required
Set these in your Vercel dashboard (Project Settings → Environment Variables):

- `NEXT_PUBLIC_API_BASE_URL`: Your backend API URL (e.g., `https://l2a-backend.onrender.com`)

### Build Configuration
- **Framework**: Next.js (auto-detected)
- **Build Command**: `npm run build` (auto-configured)
- **Output Directory**: `.next` (auto-configured)
- **Install Command**: `npm install` (auto-configured)

### Local Development
1. Copy `.env.example` to `.env.local`
2. Update `NEXT_PUBLIC_API_BASE_URL` to your local backend URL
3. Run `npm run dev`

### Production Optimization
The app includes:
- ✅ React Strict Mode
- ✅ SWC Minification
- ✅ Security headers
- ✅ TypeScript type checking
- ✅ ESLint configuration

### Connecting to Backend
Make sure your backend's `CORS_ORIGINS` environment variable includes your Vercel domain:
```
CORS_ORIGINS=https://your-app.vercel.app
```

### Testing Production Build Locally
```bash
npm run build
npm start
```

## File Structure for Deployment
```
frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── styles/
├── package.json
├── next.config.js
├── vercel.json
├── .env.example
└── README.md
```

## Notes
- Environment variables must be prefixed with `NEXT_PUBLIC_` to be available in the browser
- The `.env.local` file is not deployed (only for local development)
- Vercel automatically optimizes images and provides CDN
- The app will work with any backend URL you configure
