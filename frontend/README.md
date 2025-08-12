# Scrptoria Frontend

**Scrptoria Frontend** is a Next.js application that provides an intuitive interface for uploading PDFs and engaging in AI-powered conversations with document content.

## ✨ Features

- **PDF Upload**: Drag-and-drop PDF upload with real-time processing progress
- **AI Chat Interface**: Conversational Q&A with streaming responses
- **LaTeX Rendering**: Advanced mathematical notation support using KaTeX
- **Responsive Design**: Modern UI built with Tailwind CSS
- **Dark Theme**: Optimized for extended reading sessions

## 🚀 Deployment

## 🚀 Deployment

### Vercel Deployment (Recommended)

#### Option 1: Automatic Deployment
1. Push your code to GitHub
2. Connect your GitHub repository to Vercel
3. Vercel will automatically detect Next.js and configure build settings
4. Set environment variables in Vercel dashboard

#### Option 2: Using Vercel CLI
```bash
npm install -g vercel
vercel
```

## 🔧 Environment Variables Required
Set these in your Vercel dashboard (Project Settings → Environment Variables):

- `NEXT_PUBLIC_API_BASE_URL`: Your backend API URL (e.g., `https://scrptoria-backend.railway.app`)

## ⚙️ Build Configuration
- **Framework**: Next.js (auto-detected)
- **Build Command**: `npm run build` (auto-configured)
- **Output Directory**: `.next` (auto-configured)
- **Install Command**: `npm install` (auto-configured)

## 🛠️ Local Development
1. Copy `.env.example` to `.env.local`
2. Update `NEXT_PUBLIC_API_BASE_URL` to your local backend URL (`http://localhost:8000`)
3. Install dependencies: `npm install`
4. Run development server: `npm run dev`

## 🚀 Production Optimization
The app includes:
- ✅ React Strict Mode for better development experience
- ✅ SWC Minification for faster builds
- ✅ Security headers configuration
- ✅ TypeScript type checking
- ✅ ESLint configuration for code quality
- ✅ Tailwind CSS for optimized styling

## 🔗 Connecting to Backend
Make sure your backend's `CORS_ORIGINS` environment variable includes your Vercel domain:
```
CORS_ORIGINS=https://scrptoria.vercel.app
```

## 🧪 Testing Production Build Locally
```bash
npm run build
npm start
```

```

## 📁 File Structure for Deployment
```
frontend/
├── src/
│   ├── components/
│   │   ├── AlternativeLatexRenderer.tsx  # LaTeX/KaTeX rendering
│   │   └── ErrorBoundary.tsx            # Error handling
│   ├── pages/
│   │   ├── index.tsx                    # Main application page
│   │   ├── _app.tsx                     # Next.js app wrapper
│   │   ├── _document.tsx                # HTML document structure
│   │   └── debug.tsx                    # Debug utilities
│   └── styles/
│       └── globals.css                  # Global styles with Tailwind
├── public/
│   └── maindframe_logo.png             # Maindframe logo
├── package.json                        # Dependencies and scripts
├── next.config.js                      # Next.js configuration
├── vercel.json                         # Vercel deployment config
├── tailwind.config.js                  # Tailwind CSS configuration
├── tsconfig.json                       # TypeScript configuration
├── .env.example                        # Environment template
└── README.md
```

## 🎨 Key Technologies
- **Next.js 13+**: React framework with app router
- **TypeScript**: Type safety and better development experience
- **Tailwind CSS**: Utility-first CSS framework
- **React Dropzone**: File upload functionality
- **KaTeX**: Mathematical notation rendering
- **React Spinners**: Loading indicators

## 📝 Notes
- Environment variables must be prefixed with `NEXT_PUBLIC_` to be available in the browser
- The `.env.local` file is not deployed (only for local development)
- Vercel automatically optimizes images and provides CDN
- The app will work with any backend URL you configure
- LaTeX rendering supports complex mathematical expressions and matrices
- Real-time streaming responses provide immediate feedback to users
