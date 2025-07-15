#!/usr/bin/env python3
"""
Reddit API Client for fetching subreddit posts
"""

import requests
import json
from typing import List, Dict
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ..utils.config import Config

class RedditAPIClient:
    """Handles Reddit API interactions (Single Responsibility)"""
    
    def __init__(self, user_agent: str = ""):
        self.headers = {
            'User-Agent': user_agent or Config.REDDIT_USER_AGENT
        }
    
    def get_subreddit_posts(self, subreddit: str, limit: int = 0, sort: str = "") -> List[Dict]:
        """
        Get posts from subreddit using Reddit's JSON API
        
        Args:
            subreddit (str): Subreddit name
            limit (int): Number of posts to get
            sort (str): Sort method
            
        Returns:
            List[Dict]: List of post data
        """
        limit = limit or Config.REDDIT_API_LIMIT
        sort = sort or Config.REDDIT_API_SORT
        
        url = f"{Config.REDDIT_API_BASE_URL}/r/{subreddit}/{sort}.json?limit={limit}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=Config.REDDIT_API_TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' not in data or 'children' not in data['data']:
                raise ValueError("Unexpected API response format")
            
            return data['data']['children']
            
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error fetching data: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Error parsing JSON: {e}") 