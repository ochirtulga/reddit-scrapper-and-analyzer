#!/usr/bin/env python3
"""
Reddit Auto Scraper - Main entry point
"""

import argparse
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.config import Config
from .reddit_auto_scraper import RedditAutoScraper

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
        
        
        # Create scraper
        scraper = RedditAutoScraper(
            subreddit=subreddit
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