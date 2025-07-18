from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .logger import logger
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from datetime import datetime
from .middleware import log_middleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.api.token import token_router
from app.api.meeting import meeting_router
from app.config import settings, Settings
from app.db.mongodb import db

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...🚀🚀🚀")
    # Connect to MongoDB
    db.connect_db()
    logger.info("Connected to MongoDB")
    
    yield
    
    # Close MongoDB connection
    db.close_db()
    logger.info("Closed MongoDB connection")
    logger.info("Shutting down...")


description = """
FastAPI for SelfHelp 🚀🚀🚀

## Endpoints
* **meeting** (_handles the meeting_).
"""



fast_api = FastAPI(lifespan=lifespan,
              title="SelfHelp - API",
                description=description,
                summary="APIs to handle scheduling meetings with AI mentor",
                version="0.0.1",
                terms_of_service="http://example.com/terms/",
                contact={
                    "name": "Sameer",
                    "url": "http://github.com/3l-d1abl0",
                },
            )

# Add CORS middleware
fast_api.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware
fast_api.add_middleware(BaseHTTPMiddleware, dispatch=log_middleware)

# Include API router
fast_api.include_router(token_router, prefix=settings.API_VERSION_STR)
fast_api.include_router(meeting_router, prefix=settings.API_VERSION_STR)


# Root endpoint
@fast_api.get("/")
async def root():
    return {
        "message": "Welcome to the SelfHelp's Meeting API",
        "docs": "/api/docs",
        "version": "1.0.0"
    }

@fast_api.get("/ping")
async def health_check():
    """Health check"""
    return {
        "status": "pong",
        "timestamp": datetime.now().isoformat()
    }

# Register exception handlers
@fast_api.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Validation error handler"""
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )

@fast_api.exception_handler(500)
async def internal_exception_handler(request: Request, exc: Exception):
    """Internal exception handler"""
    logger.error(f"Internal server error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

@fast_api.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error occurred"}
    )