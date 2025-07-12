from fastapi import FastAPI, Request, status
from contextlib import asynccontextmanager
from .logger import logger

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


# Root endpoint
@fast_api.get("/")
async def root():
    return {
        "message": "Welcome to the SelfHelp's Meeting API",
        "docs": "/api/docs",
        "version": "1.0.0"
    }