#!/usr/bin/env python3
"""
File management utilities for Reddit Data Mining System
"""

import os
from datetime import datetime
from typing import List
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class FileManager:
    """File manager for handling data file operations"""
    
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.scraped_dir = os.path.join(base_dir, 'scraped')
        self.analyzed_dir = os.path.join(base_dir, 'analyzed')
        
        # Create directories
        self._create_directories()
    
    def _create_directories(self):
        """Create necessary directories"""
        directories = [
            self.scraped_dir,
            os.path.join(self.scraped_dir, 'csv'),
            os.path.join(self.scraped_dir, 'json'),
            self.analyzed_dir,
            os.path.join(self.analyzed_dir, 'csv'),
            os.path.join(self.analyzed_dir, 'json'),
            os.path.join(self.analyzed_dir, 'reports')
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def get_timestamped_filename(self, prefix: str, extension: str) -> str:
        """Generate timestamped filename"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}.{extension}"
    
    def list_files(self, subdir: str, extension: str = None) -> List[str]:
        """List files in a subdirectory"""
        if subdir == 'json':
            directory = os.path.join(self.scraped_dir, 'json')
        elif subdir == 'csv':
            directory = os.path.join(self.scraped_dir, 'csv')
        else:
            directory = os.path.join(self.analyzed_dir, subdir)
        
        if not os.path.exists(directory):
            return []
        
        files = os.listdir(directory)
        if extension:
            files = [f for f in files if f.endswith(extension)]
        
        return files 