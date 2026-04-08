import sys
from loguru import logger
from src.config.settings import LOG_LEVEL

def setup_logger():
    logger.remove()
    logger.add(
        sys.stderr, 
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
        level=LOG_LEVEL
    )
    logger.add("logs/agent.log", rotation="10 MB", level="INFO")

setup_logger()
