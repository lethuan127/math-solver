import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.endpoints import router as api_router
from .core.config import get_settings
from .core.utils import setup_logging

# Initialize settings and logging
settings = get_settings()
setup_logging(level="INFO" if not settings.debug else "DEBUG")

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    debug=settings.debug,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "message": "Math Homework Solver API",
        "version": settings.api_version,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.environment,
        "version": settings.api_version,
    }
