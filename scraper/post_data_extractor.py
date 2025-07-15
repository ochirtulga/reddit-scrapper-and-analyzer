#!/usr/bin/env python3
"""
Post Data Extractor for processing Reddit post data
"""

from datetime import datetime
from urllib.parse import urljoin
from typing import Dict
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.config import Config

class PostDataExtractor:
    """Handles post data extraction (Single Responsibility)"""
    
    @staticmethod
    def extract_post_data(post: Dict) -> Dict:
        """Extract relevant data from a Reddit post"""
        post_data = post['data']
        
        return {
            'post_id': post_data.get('id', ''),
            'title': post_data.get('title', ''),
            'author': post_data.get('author', ''),
            'score': post_data.get('score', 0),
            'upvote_ratio': post_data.get('upvote_ratio', 0),
            'num_comments': post_data.get('num_comments', 0),
            'url': post_data.get('url', ''),
            'permalink': urljoin(Config.REDDIT_API_BASE_URL, post_data.get('permalink', '')),
            'created_utc': post_data.get('created_utc', 0),
            'subreddit': post_data.get('subreddit', ''),
            'is_self': post_data.get('is_self', False),
            'is_video': post_data.get('is_video', False),
            'domain': post_data.get('domain', ''),
            'over_18': post_data.get('over_18', False),
            'spoiler': post_data.get('spoiler', False),
            'stickied': post_data.get('stickied', False),
            'scraped_at': datetime.now().isoformat()
        } 