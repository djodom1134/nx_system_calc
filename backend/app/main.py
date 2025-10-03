"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.core.config import get_settings
from app.api import calculator, config, webhooks, email, branding, projects
from app.models.base import init_db

settings = get_settings()

# Initialize database tables
init_db()

app = FastAPI(
    title="Nx System Calculator API",
    description="VMS system calculator for Network Optix deployments",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure upload directory exists
upload_dir = Path(settings.upload_dir)
upload_dir.mkdir(parents=True, exist_ok=True)

# Mount static files for uploads
app.mount("/uploads", StaticFiles(directory=str(upload_dir)), name="uploads")

# Include routers
app.include_router(calculator.router, prefix="/api/v1", tags=["calculator"])
app.include_router(config.router, prefix="/api/v1/config", tags=["configuration"])
app.include_router(webhooks.router, prefix="/api/v1", tags=["webhooks"])
app.include_router(email.router, prefix="/api/v1", tags=["email"])
app.include_router(branding.router, prefix="/api/v1/branding", tags=["branding"])
app.include_router(projects.router, prefix="/api/v1", tags=["projects"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Nx System Calculator API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "operational",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
    )

