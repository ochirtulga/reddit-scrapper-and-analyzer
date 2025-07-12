#!/usr/bin/env python3
"""
Configuration settings for Reddit Data Mining System
"""

import os

class Config:
    """Centralized configuration for the Reddit data mining system"""
    
    # Default directories
    DEFAULT_DATA_DIR = 'data'
    DEFAULT_OUTPUT_DIR = 'data/analyzed'
    DEFAULT_DB_DIR = 'data/db'
    DEFAULT_LOGS_DIR = 'data/logs'
    DEFAULT_SCRAPED_DIR = 'data/scraped'
    DEFAULT_ANALYZED_DIR = 'data/analyzed'
    
    # File paths
    DEFAULT_DB_NAME = 'reddit_scraper.db'
    DEFAULT_SCRAPER_LOG = 'reddit_scraper.log'
    DEFAULT_ANALYZER_LOG = 'word_analyzer.log'
    
    # Reddit API settings
    REDDIT_API_BASE_URL = 'https://www.reddit.com'
    REDDIT_API_TIMEOUT = 15
    REDDIT_API_LIMIT = 100
    REDDIT_API_SORT = 'new'
    REDDIT_USER_AGENT = 'RedditAutoScraper/1.0 (by /u/your_username)'
    
    # Scraping settings
    DEFAULT_SUBREDDIT = 'Python'
    DEFAULT_INTERVAL_MINUTES = 60
    MIN_INTERVAL_MINUTES = 5
    
    # Analysis settings
    MIN_WORD_LENGTH = 3
    DEFAULT_TOP_N = 50
    CONTEXT_LENGTH = 50
    
    # Database settings
    DATABASE_TABLES = {
        'scraped_posts': '''
            CREATE TABLE IF NOT EXISTS scraped_posts (
                post_id TEXT PRIMARY KEY,
                title TEXT,
                author TEXT,
                score INTEGER,
                num_comments INTEGER,
                created_utc REAL,
                scraped_at TEXT,
                subreddit TEXT
            )
        ''',
        'scraping_sessions': '''
            CREATE TABLE IF NOT EXISTS scraping_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_start TEXT,
                session_end TEXT,
                posts_scraped INTEGER,
                subreddit TEXT
            )
        '''
    }
    
    # Stop words for text analysis
    STOP_WORDS = {
        'ever', 'why', 'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 
        'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at', 
        'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she', 
        'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 
        'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 
        'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know', 
        'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 
        'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 
        'over', 'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 
        'work', 'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any', 
        'these', 'give', 'day', 'most', 'us', 'is', 'are', 'was', 'were', 'been', 
        'being', 'has', 'had', 'does', 'did', 'should', 'may', 'might', 'must', 
        'shall', 'am', 'pm', 'etc', 'vs', 'vs.', 'mr', 'mrs', 'dr', 'prof', 
        'inc', 'ltd', 'co', 'corp', 'llc', 'etc.', 'i.e.', 'e.g.', 'vs.', 
        'mr.', 'mrs.', 'dr.', 'prof.', 'inc.', 'ltd.', 'co.', 'corp.', 'llc.'
    }
    
    # Logging configuration
    LOGGING_CONFIG = {
        'level': 'INFO',
        'format': '%(asctime)s - %(levelname)s - %(message)s',
        'date_format': '%Y-%m-%d %H:%M:%S'
    }
    
    @classmethod
    def get_db_path(cls, data_dir: str = "", db_name: str = "") -> str:
        """Get database path"""
        actual_data_dir = data_dir if data_dir else cls.DEFAULT_DATA_DIR
        actual_db_name = db_name if db_name else cls.DEFAULT_DB_NAME
        db_dir = os.path.join(actual_data_dir, 'db')
        
        # Ensure database directory exists
        os.makedirs(db_dir, exist_ok=True)
        
        return os.path.join(db_dir, actual_db_name)

    @classmethod
    def get_log_path(cls, data_dir: str = "", log_name: str = "") -> str:
        """Get log file path"""
        actual_data_dir = data_dir if data_dir else cls.DEFAULT_DATA_DIR
        actual_log_name = log_name if log_name else cls.DEFAULT_SCRAPER_LOG
        logs_dir = os.path.join(actual_data_dir, 'logs')
        
        # Ensure logs directory exists
        os.makedirs(logs_dir, exist_ok=True)
        
        return os.path.join(logs_dir, actual_log_name)
    
    @classmethod
    def get_scraped_dir(cls, data_dir: str = "") -> str:
        """Get scraped data directory"""
        actual_data_dir = data_dir if data_dir else cls.DEFAULT_DATA_DIR
        return os.path.join(actual_data_dir, 'scraped')
    
    @classmethod
    def get_analyzed_dir(cls, data_dir: str = "") -> str:
        """Get analyzed data directory"""
        actual_data_dir = data_dir if data_dir else cls.DEFAULT_DATA_DIR
        return os.path.join(actual_data_dir, 'analyzed') 