#!/usr/bin/env python3
"""
Financial AI Worker - Main Application
Portfolio Analysis and Trading Platform
"""
import asyncio
import logging
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from config.settings import settings
from src.api.main import app
import uvicorn

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def create_directories():
    """Create necessary directories"""
    directories = [
        "logs",
        "data",
        "config",
        "src/brokers",
        "src/analytics", 
        "src/api",
        "src/models",
        "src/visualization",
        "src/web"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory}")


def check_environment():
    """Check environment configuration"""
    required_vars = [
        "ZERODHA_API_KEY",
        "ZERODHA_API_SECRET"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not getattr(settings, var.lower(), None):
            missing_vars.append(var)
    
    if missing_vars:
        logger.warning(f"Missing environment variables: {', '.join(missing_vars)}")
        logger.warning("Please set these variables in your .env file or environment")
        logger.warning("See env.example for reference")
    
    return len(missing_vars) == 0


def main():
    """Main application entry point"""
    logger.info("Starting Financial AI Worker...")
    
    # Create directories
    create_directories()
    
    # Check environment
    env_ok = check_environment()
    if not env_ok:
        logger.warning("Environment configuration incomplete. Some features may not work.")
    
    # Start the application
    logger.info(f"Starting server on {settings.api_host}:{settings.api_port}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"API documentation available at: http://{settings.api_host}:{settings.api_port}/docs")
    logger.info(f"Dashboard available at: http://{settings.api_host}:{settings.api_port}/")
    
    try:
        uvicorn.run(
            "src.api.main:app",
            host=settings.api_host,
            port=settings.api_port,
            reload=settings.debug,
            log_level=settings.log_level.lower()
        )
    except KeyboardInterrupt:
        logger.info("Shutting down Financial AI Worker...")
    except Exception as e:
        logger.error(f"Error starting application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

