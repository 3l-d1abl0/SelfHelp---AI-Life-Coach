from fastapi import FastAPI, Request, status
from contextlib import asynccontextmanager
from .logger import logger
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from datetime import datetime
from .middleware import log_middleware
from starlette.middleware.base import BaseHTTPMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    yield
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

fast_api.add_middleware(BaseHTTPMiddleware, dispatch=log_middleware)

## Include API router
#app.include_router(api_router, prefix=settings.API_V1_STR)


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