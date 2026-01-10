"""
FastAPI application for ISO Toolkit web interface.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from api.database.session import init_database
from api.routes import os, downloads, ws

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events.
    """
    # Startup
    logger.info("Starting ISO Toolkit API...")
    init_database()
    logger.info("Database initialized")

    yield

    # Shutdown
    logger.info("Shutting down ISO Toolkit API...")


# Create FastAPI app
app = FastAPI(
    title="ISO Toolkit API",
    description="Multi-OS ISO Downloader Toolkit - Web API",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
# Allow environment variable for deployed frontend, with localhost fallback
import os
allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else []
allowed_origins.extend([
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",  # Alternative dev server
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(os.router)
app.include_router(downloads.router)
app.include_router(ws.router)


@app.get("/")
async def root():
    """Root endpoint - API info."""
    return {
        "name": "ISO Toolkit API",
        "version": "1.0.0",
        "description": "Multi-OS ISO Downloader Toolkit",
        "docs": "/docs",
        "endpoints": {
            "os": "/api/os",
            "downloads": "/api/downloads",
            "websocket": "/api/ws/downloads",
        },
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "iso-toolkit-api",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
