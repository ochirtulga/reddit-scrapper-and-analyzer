#!/usr/bin/env python3
"""
Reddit Auto Scraper - Main scraper orchestrator
"""

import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.config import Config
from utils.database import DatabaseManager
from utils.logger import LoggerManager
from utils.text_processor import TextProcessor
from .reddit_api_client import RedditAPIClient
from .post_data_extractor import PostDataExtractor

class RedditAutoScraper:
    """Main scraper class that orchestrates the scraping process"""

    def __init__(self, subreddit: str = "", num_posts: int = 20):
        """
        Initialize the automated Reddit scraper
        
        Args:
            subreddit (str): Subreddit name (without r/)
            num_posts (int): Number of posts to fetch
        """
        self.subreddit = subreddit or Config.DEFAULT_SUBREDDIT
        self.num_posts = num_posts
        
        # Initialize components
        self.log_path = Config.get_log_path(Config.DEFAULT_SCRAPER_LOG, "scraper")
        
        # Setup utilities
        self.logger = LoggerManager.setup_logger('reddit_scraper', self.log_path)
        self.db_manager = DatabaseManager()
        self.api_client = RedditAPIClient()
        
        # Initialize database
        if not self.db_manager.init_database():
            raise RuntimeError("Failed to initialize database")
    
    def get_last_scraped_timestamp(self) -> Optional[float]:
        """Get the timestamp of the last scraped post"""
        return self.db_manager.get_last_timestamp(self.subreddit)
    
    def is_post_new(self, post_id: str, created_utc: float, last_timestamp: Optional[float]) -> bool:
        """Check if a post is new"""
        # Check if post already exists
        if self.db_manager.post_exists(post_id):
            return False
        
        # Check if post is newer than last scraped timestamp
        if last_timestamp and created_utc <= last_timestamp:
            return False
        
        return True
    
    def scrape_new_posts(self) -> List[Dict]:
        """Scrape only new posts since last run"""
        session_start = datetime.now().isoformat()
        self.logger.info(f"Starting scraping session for r/{self.subreddit}")
        
        # Get last scraped timestamp
        last_timestamp = self.get_last_scraped_timestamp()
        if last_timestamp:
            last_time = datetime.fromtimestamp(last_timestamp)
            self.logger.info(f"Last scraped post was from: {last_time}")
        else:
            self.logger.info("No previous scraping history found")
        
        # Get posts from Reddit API
        try:
            posts = self.api_client.get_subreddit_posts(self.subreddit, limit=self.num_posts)
            self.logger.info(f"Successfully fetched {len(posts)} posts")
        except Exception as e:
            self.logger.error(f"Error fetching posts: {e}")
            self.db_manager.save_session(session_start, 0, self.subreddit)
            return []
        
        # Filter for new posts only
        new_posts_data = []
        for post in posts:
            post_data = PostDataExtractor.extract_post_data(post)
            
            if self.is_post_new(post_data['post_id'], post_data['created_utc'], last_timestamp):
                new_posts_data.append(post_data)
                self.db_manager.save_post(post_data)
                self.logger.info(f"New post: {post_data['title'][:50]}...")
            else:
                self.logger.debug(f"Skipping existing post: {post_data['title'][:50]}...")
        
        # Update word frequencies for new posts
        if new_posts_data:
            self.update_word_frequencies(new_posts_data)
        
        # Save data to files
        # (REMOVED: Only store in PostgreSQL)
        if new_posts_data:
            # Show summary
            print(f"\n=== Scraping Summary (r/{self.subreddit}) ===")
            print(f"Total posts fetched: {len(posts)}")
            print(f"New posts found: {len(new_posts_data)}")
            print(f"Data saved to: PostgreSQL database")
            print(f"Word frequencies updated")
            # Show sample new posts
            if new_posts_data:
                print(f"\n=== New Posts Found ===")
                for i, post in enumerate(new_posts_data[:3], 1):
                    print(f"\n{i}. {post['title'][:80]}...")
                    print(f"   Author: {post['author']}")
                    print(f"   Score: {post['score']} | Comments: {post['num_comments']}")
                    print(f"   Created: {datetime.fromtimestamp(post['created_utc'])}")
        else:
            print(f"\n=== No New Posts Found ===")
            print(f"All {len(posts)} fetched posts were already scraped")
        
        # Save session info
        self.db_manager.save_session(session_start, len(new_posts_data), self.subreddit)
        # Add subreddit to scraped_subreddits
        self.db_manager.add_scraped_subreddit(self.subreddit)
        return new_posts_data
    
    def update_word_frequencies(self, new_posts: List[Dict]):
        """Update word frequencies for new posts"""
        try:
            text_processor = TextProcessor()
            new_word_frequencies = {}
            
            # Process each new post
            for post in new_posts:
                # Extract text from title
                title_text = post.get('title', '')
                if title_text:
                    word_freqs = text_processor.get_word_frequencies(title_text)
                    for word, count in word_freqs.items():
                        new_word_frequencies[word] = new_word_frequencies.get(word, 0) + count
            
            # Update database with new word frequencies
            if new_word_frequencies:
                self.db_manager.update_word_frequencies(new_word_frequencies)
                self.logger.info(f"Updated word frequencies for {len(new_word_frequencies)} words")
            
        except Exception as e:
            self.logger.error(f"Error updating word frequencies: {e}")
    
    def run_scraping_job(self):
        """Main scraping job"""
        try:
            self.logger.info("=" * 50)
            self.logger.info(f"Starting scraping job for r/{self.subreddit}")
            
            new_posts = self.scrape_new_posts()
            
            self.logger.info(f"Scraping job completed. Found {len(new_posts)} new posts")
            self.logger.info("=" * 50)
            
            return new_posts
            
        except Exception as e:
            self.logger.error(f"Error in scraping job: {e}")
            return []
    
    def start_auto_scraper(self, interval_minutes: int = 0):
        """Start the automated scraper"""
        interval_minutes = interval_minutes or Config.DEFAULT_INTERVAL_MINUTES
        
        print(f"=== Reddit Auto Scraper ===")
        print(f"Subreddit: r/{self.subreddit}")
        print(f"Interval: Every {interval_minutes} minute(s)")
        print(f"Output directory: {self.output_dir}")
        print(f"Database: {self.db_path}")
        print(f"Log file: {self.log_path}")
        print(f"\nStarting auto scraper... (Press Ctrl+C to stop)")
        print(f"Next run in {interval_minutes} minute(s)")
        
        # Run initial scraping
        self.run_scraping_job()
        
        # Convert minutes to seconds
        interval_seconds = interval_minutes * 60
        
        # Keep the scraper running
        try:
            while True:
                print(f"\nWaiting {interval_minutes} minute(s) until next scrape...")
                print(f"Next scrape at: {datetime.now() + timedelta(minutes=interval_minutes)}")
                
                # Sleep for the interval
                time.sleep(interval_seconds)
                
                # Run scraping job
                self.run_scraping_job()
                
        except KeyboardInterrupt:
            print("\n\nAuto scraper stopped by user")
            self.logger.info("Auto scraper stopped by user") 