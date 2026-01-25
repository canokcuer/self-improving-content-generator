"""
FastAPI Application Entry Point

This is the main entry point for the secure API backend.
Run with: uvicorn content_assistant.api.main:app --reload
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    # Startup
    logger.info("Starting TheLifeCo Content API...")

    # Validate required environment variables
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_KEY",
        "SUPABASE_JWT_SECRET",
    ]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        logger.error(f"Missing required environment variables: {missing}")
        raise RuntimeError(f"Missing environment variables: {missing}")

    logger.info("Environment validated successfully")

    yield

    # Shutdown
    logger.info("Shutting down TheLifeCo Content API...")


# Create FastAPI application
app = FastAPI(
    title="TheLifeCo Content API",
    description="Secure API backend for the Self-Improving Content Generator",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for Streamlit frontend
# In production, replace with specific origins
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8501").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions without exposing internal details."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again."},
    )


# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "service": "thelifeco-content-api"}


# Root endpoint
@app.get("/", tags=["System"])
async def root():
    """API root - provides basic information."""
    return {
        "name": "TheLifeCo Content API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


# Import and include routers
from content_assistant.api.routes import conversations, generations, admin

app.include_router(conversations.router, prefix="/api/conversations", tags=["Conversations"])
app.include_router(generations.router, prefix="/api/generations", tags=["Generations"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "content_assistant.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
