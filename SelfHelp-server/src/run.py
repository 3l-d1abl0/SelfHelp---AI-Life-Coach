import uvicorn
from app.config import get_settings, Settings
from app.logger import logger

settings: Settings = get_settings()

if __name__ == "__main__":
    
    logger.info('Starting uvicorn ... ')
    try:
        uvicorn.run("app.main:fast_api", host="0.0.0.0", port=settings.PORT, reload=settings.RELOAD)

    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
    except Exception as e:
        logger.error("Server error: %s",e)
        sys.exit(1)
