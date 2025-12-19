# Getting Started with AI UGC Video Platform

This guide will help you set up and run the AI UGC Video Platform locally.

## Prerequisites

### Required Software
- Python 3.10 or higher
- Node.js 18 or higher
- PostgreSQL 14+
- Redis 7+
- Git

### Hardware Requirements
- **Minimum**: 16GB RAM, CPU-only (slower)
- **Recommended**: 32GB RAM, NVIDIA GPU with 12GB+ VRAM
- **Storage**: 20GB+ free space (for AI models)

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd aniketsays21
```

### 2. Backend Setup

#### Install Dependencies

```bash
cd backend
python -m venv venv

# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

pip install -r requirements.txt
```

#### Install Playwright Browsers

```bash
playwright install chromium
```

#### Setup Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and configure:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ugc_platform

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/2
CELERY_RESULT_BACKEND=redis://localhost:6379/3

# Important: Generate a secure secret key
SECRET_KEY=your-secret-key-here

# AI Models
USE_LOCAL_MODELS=True  # Set to False to use cloud APIs
```

#### Initialize Database

```bash
# Create PostgreSQL database
createdb ugc_platform

# Initialize tables
python -c "from models.database import init_db; init_db()"

# Seed initial data
cd ../scripts
python seed_data.py
```

### 3. Frontend Setup

```bash
cd ../frontend
npm install
```

### 4. Download AI Models (First Time Only)

This step is required if you're using local models. It will download several GB of data.

```bash
# Install Bark for voice synthesis
pip install git+https://github.com/suno-ai/bark.git

# On first run, Bark will automatically download models
# This happens when you first generate a video
```

## Running the Application

You'll need **3 terminal windows**:

### Terminal 1: Backend Server

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn api.main:app --reload
```

The API will be available at: http://localhost:8000
API documentation: http://localhost:8000/docs

### Terminal 2: Celery Worker

```bash
cd backend
source venv/bin/activate
celery -A services.worker worker --loglevel=info
```

This handles background video generation jobs.

### Terminal 3: Frontend Dev Server

```bash
cd frontend
npm run dev
```

The frontend will be available at: http://localhost:5173

## Using the Platform

### Step-by-Step Workflow

1. **Product Scraping** (Optional)
   - Enter a product URL (Amazon, Shopify, etc.)
   - The system will extract images and description
   - Or skip this step if you don't have a product URL

2. **Select Model Image**
   - Upload a photo of a person (model)
   - This will be the "UGC creator" in your video
   - Tip: Use clear, front-facing images for best results

3. **Choose Background**
   - Select from available backgrounds
   - Upload custom backgrounds via API (see API docs)

4. **Select Action**
   - Choose what movement/action the model performs
   - Default actions include: Showcase, Presentation, Demo, etc.

5. **Configure Voice**
   - Enter the script/text to be spoken
   - Select emotion (happy, excited, neutral, etc.)
   - Adjust video duration (3-30 seconds)

6. **Generate Video**
   - Review your configuration
   - Click "Generate Video"
   - Wait 2-5 minutes for processing
   - Download your video!

## Troubleshooting

### Common Issues

#### Database Connection Error

```bash
# Make sure PostgreSQL is running
sudo systemctl status postgresql

# Or on Mac:
brew services list
```

#### Redis Connection Error

```bash
# Make sure Redis is running
sudo systemctl status redis

# Or start it:
sudo systemctl start redis
```

#### GPU Not Detected

If you have a GPU but it's not being used:

```bash
# Check CUDA installation
python -c "import torch; print(torch.cuda.is_available())"

# Install CUDA-compatible PyTorch
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

#### Video Generation Fails

Check the Celery worker logs for detailed error messages. Common issues:

1. **Out of memory**: Reduce video resolution or use CPU
2. **Missing models**: First run downloads models automatically
3. **FFmpeg not found**: Install ffmpeg
   ```bash
   # Ubuntu/Debian
   sudo apt-get install ffmpeg

   # Mac
   brew install ffmpeg

   # Windows
   # Download from https://ffmpeg.org/download.html
   ```

## API Usage

### Upload Background

```bash
curl -X POST http://localhost:8000/api/backgrounds \
  -F "file=@/path/to/background.jpg" \
  -F "name=My Background" \
  -F "category=Custom"
```

### Upload Model Image

```bash
curl -X POST http://localhost:8000/api/upload-model \
  -F "file=@/path/to/model.jpg" \
  -F "name=Model Name"
```

### Generate Video via API

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model_image_id": 1,
    "background_id": 1,
    "action_id": 1,
    "audio_text": "This product is amazing!",
    "emotion": "excited",
    "duration": 5.0
  }'
```

## Cost Information

### Free Tier (Recommended for Development)

- All models run locally
- **Cost**: $0/month
- **Speed**: 2-5 minutes per video
- **Requirements**: GPU with 12GB+ VRAM recommended

### Cloud Tier (For Production)

Using Replicate API for faster generation:

- Set `USE_LOCAL_MODELS=False` in `.env`
- Add `REPLICATE_API_TOKEN` to `.env`
- **Cost**: ~$0.15-0.30 per video
- **Speed**: 1-2 minutes per video

### Hybrid Approach

- Voice: Local (Bark) - Free
- Video: Cloud (Replicate) - ~$0.10/video
- Best balance of cost and speed

## Next Steps

### Production Deployment

1. Use a production-grade WSGI server (Gunicorn)
2. Set up proper PostgreSQL with connection pooling
3. Use Redis cluster for high availability
4. Deploy Celery workers on separate machines
5. Use cloud storage (S3/R2) for videos
6. Add CDN for video delivery
7. Implement rate limiting and authentication

### Scaling

- Add more Celery workers for concurrent processing
- Use GPU instances for faster local generation
- Implement video caching to avoid regeneration
- Add queue prioritization for paid users

### Customization

- Add custom actions (edit `scripts/seed_data.py`)
- Fine-tune AI models for better quality
- Customize UI theme in `frontend/tailwind.config.js`
- Add analytics and tracking

## Resources

### AI Models Documentation

- **Bark**: https://github.com/suno-ai/bark
- **MagicAnimate**: https://github.com/magic-research/magic-animate
- **Rembg**: https://github.com/danielgatis/rembg
- **Replicate**: https://replicate.com/docs

### Framework Documentation

- **FastAPI**: https://fastapi.tiangolo.com/
- **React**: https://react.dev/
- **Celery**: https://docs.celeryproject.org/
- **SQLAlchemy**: https://docs.sqlalchemy.org/

## Support

For issues and questions:
1. Check the [GitHub Issues](https://github.com/your-repo/issues)
2. Review the AI_MODELS_GUIDE.md for model details
3. Check API documentation at http://localhost:8000/docs

## License

MIT License - see LICENSE file for details
