#!/usr/bin/env python3
"""
Reddit Auto Scraper
"""

import requests
import json
import time
import argparse
from datetime import datetime, timedelta
from urllib.parse import urljoin
from typing import List, Dict, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import Config
from utils.database import DatabaseManager
from utils.file_manager import FileManager
from utils.logger import LoggerManager

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

class RedditAutoScraper:
    """Main scraper class that orchestrates the scraping process"""

    def __init__(self, subreddit: str = "", output_dir: str = "", db_path: str = ""):
        """
        Initialize the automated Reddit scraper
        
        Args:
            subreddit (str): Subreddit name (without r/)
            output_dir (str): Directory to save data
            db_path (str): SQLite database path
        """
        self.subreddit = subreddit or Config.DEFAULT_SUBREDDIT
        self.output_dir = output_dir or Config.DEFAULT_DATA_DIR
        
        # Initialize components
        self.db_path = db_path or Config.get_db_path(self.output_dir)
        self.log_path = Config.get_log_path(self.output_dir, Config.DEFAULT_SCRAPER_LOG)
        
        # Setup utilities
        self.logger = LoggerManager.setup_logger('reddit_scraper', self.log_path)
        self.db_manager = DatabaseManager(self.db_path)
        self.file_manager = FileManager(self.output_dir)
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
            posts = self.api_client.get_subreddit_posts(self.subreddit)
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
        
        # Save data to files
        if new_posts_data:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"reddit_auto_{self.subreddit}_{timestamp}"
            
            # Save to files
            json_file = self.file_manager.save_json_data(new_posts_data, f"{base_filename}.json", 'json')
            csv_file = self.file_manager.save_csv_data(new_posts_data, f"{base_filename}.csv", 'csv')
            
            self.logger.info(f"Data saved to {json_file} and {csv_file}")
            
            # Show summary
            print(f"\n=== Scraping Summary (r/{self.subreddit}) ===")
            print(f"Total posts fetched: {len(posts)}")
            print(f"New posts found: {len(new_posts_data)}")
            print(f"Data saved to: {self.file_manager.scraped_dir}/")
            
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
        
        return new_posts_data
    
    def run_scraping_job(self):
        """Main scraping job"""
        try:
            self.logger.info("=" * 50)
            self.logger.info(f"Starting scraping job for r/{self.subreddit}")
            
            new_posts = self.scrape_new_posts()
            
            self.logger.info(f"Scraping job completed. Found {len(new_posts)} new posts")
            self.logger.info("=" * 50)
            
        except Exception as e:
            self.logger.error(f"Error in scraping job: {e}")
    
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

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Reddit Auto Scraper')
    parser.add_argument('--once', action='store_true', 
                       help='Run scraper once and exit (no continuous mode)')
    parser.add_argument('--subreddit', type=str, 
                       help='Subreddit name (without r/)')
    parser.add_argument('--interval', type=int, 
                       help='Scraping interval in minutes')
    parser.add_argument('--output-dir', type=str, 
                       help='Output directory')
    
    args = parser.parse_args()
    
    print("=== Reddit Auto Scraper Setup ===\n")
    
    try:
        # Get configuration (use args if provided, otherwise prompt)
        subreddit = args.subreddit or input("Enter subreddit name (without r/): ").strip()
        if not subreddit:
            subreddit = Config.DEFAULT_SUBREDDIT
        
        if args.interval:
            interval_minutes = args.interval
        else:
            interval_input = input(f"Scraping interval in minutes (default: {Config.DEFAULT_INTERVAL_MINUTES}): ").strip()
            interval_minutes = int(float(interval_input)) if interval_input else Config.DEFAULT_INTERVAL_MINUTES
        
        output_dir = args.output_dir or input(f"Output directory (default: {Config.DEFAULT_DATA_DIR}): ").strip()
        if not output_dir:
            output_dir = Config.DEFAULT_DATA_DIR
        
        db_path_input = input("Database path (default: auto-create): ").strip()
        db_path = db_path_input if db_path_input else None
        
        # Create scraper
        scraper = RedditAutoScraper(
            subreddit=subreddit,
            output_dir=output_dir,
            db_path=db_path or Config.get_db_path(output_dir)
        )
        
        # Show database stats
        stats = scraper.db_manager.get_database_stats()
        if stats.get('total_posts', 0) > 0:
            print(f"\nCurrent database: {stats['total_posts']} posts")
            if stats.get('posts_by_subreddit'):
                for subreddit_name, count in stats['posts_by_subreddit'].items():
                    print(f"   r/{subreddit_name}: {count} posts")
        
        print("\nTip: Use 'python3 utils/manage_database.py' to clean the database")
        
        if args.once:
            # Run once and exit
            print(f"\n=== Running Scraper Once (r/{subreddit}) ===")
            scraper.run_scraping_job()
            print("\nScraping completed!")
        else:
            # Run continuous mode
            scraper.start_auto_scraper(interval_minutes)
        
    except (KeyboardInterrupt, EOFError):
        print("\n\nSetup cancelled by user.")
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    main() 