"""
Global Configuration for Application
"""
import os
import logging

# Get configuration from environment
REDIS_URL = os.getenv("DATABASE_URI", "redis://:@localhost:6379/0")
LOGGING_LEVEL = logging.INFO
