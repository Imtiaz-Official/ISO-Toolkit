"""
FastAPI application for ISO Toolkit web interface.
Serves both API endpoints and the frontend React app.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import logging
import os as os_module
from pathlib import Path

from api.database.session import init_database
from api.routes import os, downloads, ws, auth, analytics, admin_iso, admin_settings

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
    frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
    if frontend_dist.exists():
        logger.info(f"Frontend dist found at {frontend_dist}")
    else:
        logger.warning(f"Frontend dist folder not found at {frontend_dist}")
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
allowed_origins = os_module.getenv("ALLOWED_ORIGINS", "").split(",") if os_module.getenv("ALLOWED_ORIGINS") else []
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
app.include_router(auth.router)
app.include_router(analytics.router)
app.include_router(admin_iso.router)
app.include_router(admin_settings.router)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "iso-toolkit",
    }


@app.get("/api")
async def api_info():
    """API info endpoint."""
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


@app.get("/")
async def root():
    """Root endpoint - serve frontend or return API info."""
    frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
    index_path = frontend_dist / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
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


@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def catch_all(request: Request, full_path: str):
    """
    Catch-all route for SPA support.
    Serves static assets and index.html for non-API routes.
    """
    frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"

    # Serve static assets (CSS, JS, images)
    # Handle both "assets/" and "/assets/" formats (index.html uses leading slashes)
    asset_path_relative = full_path.lstrip("/")
    if asset_path_relative.startswith("assets/"):
        asset_path = frontend_dist / asset_path_relative
        if asset_path.exists() and asset_path.is_file():
            return FileResponse(str(asset_path))
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Asset not found")

    # Skip websocket routes
    if full_path.startswith("api/ws/"):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Not found")

    # If it's an API route, let it 404 naturally
    if full_path.startswith("api/"):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="API endpoint not found")

    # For all other routes, serve index.html for SPA routing
    index_path = frontend_dist / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))

    return {"error": "Frontend not built. Run: cd frontend && npm run build"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
