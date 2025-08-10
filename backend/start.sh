#!/usr/bin/env bash
set -Eeuo pipefail

# cd to this script's directory (robust)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Determine mode from environment or argument
MODE="${1:-${ENVIRONMENT:-development}}"

echo "🚀 Starting L2A Backend Server (${MODE} mode)..."

# Load environment variables
if [[ -f ".env" && "$MODE" == "development" ]]; then
  echo "📋 Loading environment variables from .env..."
  set -a
  # shellcheck disable=SC1091
  source ".env"
  set +a
elif [[ "$MODE" == "development" ]]; then
  echo "⚠️  No .env file found for development mode."
  echo "👉 Create .env file with GOOGLE_API_KEY"
  exit 1
fi

# Validate required environment variables
: "${GOOGLE_API_KEY:?Set GOOGLE_API_KEY environment variable}"

# Set environment defaults based on mode
if [[ "$MODE" == "production" ]]; then
  export ENVIRONMENT="production"
  export CORS_ORIGINS="${CORS_ORIGINS:-https://your-frontend-domain.com}"
  # Create necessary directories for production
  mkdir -p uploads data logs
else
  export ENVIRONMENT="${ENVIRONMENT:-development}"
  export CORS_ORIGINS="${CORS_ORIGINS:-http://localhost:3000,http://127.0.0.1:3000}"
  
  # Development mode checks
  if [[ ! -d "bend" || ! -d "app" ]]; then
    echo "❌ Error: Expected 'bend' (venv) and 'app' directories here."
    echo "👉 Run: python -m venv bend && source bend/bin/activate && pip install -r requirements.txt"
    exit 1
  fi
  
  if [[ ! -x "bend/bin/uvicorn" ]]; then
    echo "❌ Error: bend/bin/uvicorn not found or not executable."
    echo "👉 Activate venv and: pip install -r requirements.txt"
    exit 1
  fi
fi

echo "🔑 GOOGLE_API_KEY configured: $([[ -n "${GOOGLE_API_KEY:-}" ]] && echo yes || echo no)"

# Start server based on mode
if [[ "$MODE" == "production" ]]; then
  echo "🌐 Starting production server on port ${PORT:-8000}"
  exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "${PORT:-8000}" \
    --workers 1 \
    --access-log \
    --log-level info
else
  echo "🌐 Starting development server: http://localhost:8000"
  echo "📊 API docs: http://localhost:8000/docs"
  echo "📂 Watching only the 'app' directory for changes..."
  
  # Extra safety: tell Watchfiles to ignore noisy dirs
  export WATCHFILES_IGNORE="**/site-packages/**,**/__pycache__/**,bend/**,.venv/**"
  
  exec ./bend/bin/uvicorn app.main:app \
    --host 0.0.0.0 --port 8000 \
    --reload --reload-dir app
fi
