#!/usr/bin/env python3
"""
Logging utilities for Reddit Data Mining System
"""

import logging
import os
import sys
from typing import Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config

class LoggerManager:
    """Centralized logging manager"""
    
    _loggers = {}
    
    @classmethod
    def setup_logger(cls, name: str, log_file: str, level: str = "INFO") -> logging.Logger:
        """Setup a logger with file and console handlers"""
        if name in cls._loggers:
            return cls._loggers[name]
        
        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level or Config.LOGGING_CONFIG['level']))
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            Config.LOGGING_CONFIG['format'],
            datefmt=Config.LOGGING_CONFIG['date_format']
        )
        
        # Create file handler
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        cls._loggers[name] = logger
        return logger
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Get an existing logger or create a new one"""
        if name in cls._loggers:
            return cls._loggers[name]
        
        # Create a default logger if not found
        return cls.setup_logger(name, Config.get_log_path()) 