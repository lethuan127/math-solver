"""Main FastAPI application with modular architecture."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .modules.math_solving.presentation.endpoints import router as math_solving_router
from .modules.shared.config import get_settings
from .modules.shared.utils import setup_logging

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
app.include_router(math_solving_router, prefix="/api/v1", tags=["Math Solving"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Math Homework Solver API",
        "version": settings.api_version,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
