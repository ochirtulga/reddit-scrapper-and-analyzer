#!/usr/bin/env python3
"""
File management utilities for Reddit Data Mining System
"""

import os
import json
import csv
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import Config

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
    
    def save_json_data(self, data: List[Dict[str, Any]], filename: str, subdir: str = 'json') -> str:
        """Save data to JSON file"""
        if subdir == 'json':
            filepath = os.path.join(self.scraped_dir, 'json', filename)
        else:
            filepath = os.path.join(self.analyzed_dir, 'json', filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return filepath
        except Exception as e:
            raise IOError(f"Error saving JSON file {filepath}: {e}")
    
    def save_csv_data(self, data: List[Dict[str, Any]], filename: str, subdir: str = 'csv') -> str:
        """Save data to CSV file"""
        if subdir == 'csv':
            filepath = os.path.join(self.scraped_dir, 'csv', filename)
        else:
            filepath = os.path.join(self.analyzed_dir, 'csv', filename)
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                if data:
                    fieldnames = data[0].keys()
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data)
            return filepath
        except Exception as e:
            raise IOError(f"Error saving CSV file {filepath}: {e}")
    
    def load_json_data(self, filename: str, subdir: str = 'json') -> List[Dict[str, Any]]:
        """Load data from JSON file"""
        if subdir == 'json':
            filepath = os.path.join(self.scraped_dir, 'json', filename)
        else:
            filepath = os.path.join(self.analyzed_dir, 'json', filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else [data]
        except Exception as e:
            raise IOError(f"Error loading JSON file {filepath}: {e}")
    
    def load_csv_data(self, filename: str, subdir: str = 'csv') -> List[Dict[str, Any]]:
        """Load data from CSV file"""
        if subdir == 'csv':
            filepath = os.path.join(self.scraped_dir, 'csv', filename)
        else:
            filepath = os.path.join(self.analyzed_dir, 'csv', filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader)
        except Exception as e:
            raise IOError(f"Error loading CSV file {filepath}: {e}")
    
    def save_report(self, content: str, filename: str) -> str:
        """Save text report"""
        filepath = os.path.join(self.analyzed_dir, 'reports', filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return filepath
        except Exception as e:
            raise IOError(f"Error saving report {filepath}: {e}")
    
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