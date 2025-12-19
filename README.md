# AI UGC Video Platform

Generate high-quality AI-powered User Generated Content videos with custom models, backgrounds, and voices.

## Features

- 🛍️ **Product Scraping**: Extract images and descriptions from product URLs
- 👤 **Custom Models**: Upload or select model images
- 🎬 **Background Selection**: Choose from pre-loaded backgrounds
- 🎭 **Action Control**: Define model actions and movements
- 🎤 **Voice Synthesis**: Select/upload audio with emotional control
- 🎥 **Video Generation**: AI-powered video creation

## Tech Stack

### Backend
- FastAPI (Python 3.10+)
- PostgreSQL
- Redis
- Celery

### Frontend
- React 18
- TailwindCSS
- Axios

### AI Models (Free/Open Source)
- **Video**: MagicAnimate, AnimateDiff
- **Voice**: Bark, Coqui TTS
- **Scraping**: Playwright, BeautifulSoup
- **Image**: Rembg, SAM

## Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL
- Redis
- GPU with 12GB+ VRAM (for local AI processing)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run migrations
alembic upgrade head

# Start backend
uvicorn api.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### AI Pipeline Setup

```bash
cd ai_pipeline
pip install -r requirements.txt

# Download models (this will take some time)
python scripts/download_models.py
```

## Usage

1. **Start Services**:
   ```bash
   # Terminal 1: Backend
   cd backend && uvicorn api.main:app --reload

   # Terminal 2: Celery Worker
   cd backend && celery -A services.worker worker --loglevel=info

   # Terminal 3: Frontend
   cd frontend && npm run dev
   ```

2. **Access Application**:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## API Endpoints

- `POST /api/scrape`: Scrape product from URL
- `POST /api/upload-model`: Upload model image
- `GET /api/backgrounds`: Get available backgrounds
- `GET /api/actions`: Get available actions
- `POST /api/generate`: Generate video
- `GET /api/video/{id}`: Get video status/result

## Configuration

See `.env.example` for all configuration options.

## Cost Estimation

- **Free Tier**: $0/month (self-hosted models)
- **Budget Tier**: ~$0.15-0.30 per video (Replicate API)
- **Premium Tier**: ~$0.50-1.00 per video (ElevenLabs + Runway)

## Development Roadmap

- [x] Project structure
- [ ] Product scraper
- [ ] Model management
- [ ] Background system
- [ ] Voice synthesis integration
- [ ] Video generation pipeline
- [ ] Frontend UI
- [ ] Queue system
- [ ] Caching layer
- [ ] Production deployment

## License

MIT

## Contributing

Pull requests are welcome!
