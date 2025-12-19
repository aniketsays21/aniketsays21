from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
from models.database import init_db

# Initialize FastAPI app
app = FastAPI(
    title=f"{settings.APP_NAME} - Test Mode",
    debug=settings.DEBUG,
    version="1.0.0-test"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Events
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    print(f"🚀 {settings.APP_NAME} started in TEST MODE")
    print(f"📊 Database: {settings.DATABASE_URL}")
    print(f"🌐 Server: http://localhost:{settings.PORT}")
    print(f"📖 API Docs: http://localhost:{settings.PORT}/docs")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("👋 Shutting down...")

# Health check
@app.get("/")
async def root():
    return {
        "name": f"{settings.APP_NAME} - Test Mode",
        "version": "1.0.0-test",
        "status": "running",
        "message": "Backend is running! Visit /docs for API documentation"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "mode": "test"
    }

# Simple test endpoints
@app.get("/api/test")
async def test_endpoint():
    return {
        "message": "API is working!",
        "endpoints": [
            {"path": "/", "description": "Root endpoint"},
            {"path": "/health", "description": "Health check"},
            {"path": "/docs", "description": "Interactive API documentation"},
            {"path": "/api/test", "description": "Test endpoint"},
        ]
    }

@app.get("/api/backgrounds")
async def list_backgrounds():
    """Mock backgrounds endpoint"""
    return [
        {"id": 1, "name": "Beach Background", "category": "outdoor"},
        {"id": 2, "name": "Studio Background", "category": "indoor"},
        {"id": 3, "name": "City Background", "category": "urban"}
    ]

@app.get("/api/actions")
async def list_actions():
    """Mock actions endpoint"""
    return [
        {"id": 1, "name": "Wave", "duration": 2.0},
        {"id": 2, "name": "Point", "duration": 1.5},
        {"id": 3, "name": "Dance", "duration": 3.0}
    ]

@app.get("/api/voices")
async def list_voices():
    """Mock voices endpoint"""
    return [
        {"id": 1, "name": "Default Voice", "emotion": "neutral"},
        {"id": 2, "name": "Happy Voice", "emotion": "happy"},
        {"id": 3, "name": "Excited Voice", "emotion": "excited"}
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_test:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
