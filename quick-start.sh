#!/bin/bash

# AI UGC Video Platform - Quick Start Script
# This script helps you set up the platform quickly

set -e

echo "🚀 AI UGC Video Platform - Quick Start"
echo "======================================="
echo ""

# Check prerequisites
echo "Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.10+"
    exit 1
fi
echo "✓ Python found: $(python3 --version)"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi
echo "✓ Node.js found: $(node --version)"

# Check PostgreSQL
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL not found. You'll need to install it separately."
else
    echo "✓ PostgreSQL found"
fi

# Check Redis
if ! command -v redis-cli &> /dev/null; then
    echo "⚠️  Redis not found. You'll need to install it separately."
else
    echo "✓ Redis found"
fi

echo ""
read -p "Do you want to continue with setup? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# Backend setup
echo ""
echo "📦 Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies (this may take a few minutes)..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo "Installing Playwright..."
playwright install chromium

# Environment setup
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit backend/.env with your configuration"
    echo "   Especially: DATABASE_URL, SECRET_KEY"
fi

cd ..

# Frontend setup
echo ""
echo "📦 Setting up frontend..."
cd frontend

echo "Installing Node dependencies..."
npm install --silent

cd ..

# Database setup
echo ""
read -p "Do you want to initialize the database now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Initializing database..."
    cd backend
    source venv/bin/activate
    python -c "from models.database import init_db; init_db()"

    echo "Seeding initial data..."
    cd ../scripts
    python seed_data.py
    cd ..
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the application, open 3 terminal windows:"
echo ""
echo "Terminal 1 - Backend:"
echo "  cd backend && source venv/bin/activate && uvicorn api.main:app --reload"
echo ""
echo "Terminal 2 - Celery Worker:"
echo "  cd backend && source venv/bin/activate && celery -A services.worker worker --loglevel=info"
echo ""
echo "Terminal 3 - Frontend:"
echo "  cd frontend && npm run dev"
echo ""
echo "Then open: http://localhost:5173"
echo ""
echo "For detailed instructions, see GETTING_STARTED.md"
