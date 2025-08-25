from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

from database import engine, Base
from routers import auth, materials, schedules, quizzes, performance, sessions
from services.ml_service import MLService

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Personalized Study Scheduler API",
    description="AI-powered personalized learning and study scheduling platform with ML-driven adaptive algorithms",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(materials.router, prefix="/materials", tags=["materials"])
app.include_router(schedules.router, prefix="/schedules", tags=["schedules"])
app.include_router(quizzes.router, prefix="/quizzes", tags=["quizzes"])
app.include_router(performance.router, prefix="/performance", tags=["performance"])
app.include_router(sessions.router, prefix="/sessions", tags=["sessions"])

@app.get("/")
async def root():
    return {
        "message": "Personalized Study Scheduler API", 
        "version": "2.0.0",
        "features": [
            "Half-Life Regression scheduling",
            "ML-driven quiz generation", 
            "Advanced learning analytics",
            "Cognitive load optimization",
            "Adaptive difficulty progression"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
