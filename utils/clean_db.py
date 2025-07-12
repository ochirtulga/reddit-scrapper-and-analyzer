#!/usr/bin/env python3
"""
Quick Database Cleaning Tool
Simple command-line interface for database operations
"""

import sys
import os
import argparse
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.config import Config
from utils.database import DatabaseManager
from utils.logger import LoggerManager

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Quick Reddit Database Management')
    parser.add_argument('action', choices=['stats', 'clean', 'reset'], 
                       help='Action to perform')
    parser.add_argument('--subreddit', '-s', type=str, 
                       help='Subreddit name (for cleaning specific subreddit)')
    parser.add_argument('--days', '-d', type=int, 
                       help='Remove posts older than X days')
    parser.add_argument('--force', '-f', action='store_true', 
                       help='Skip confirmation prompts')
    
    args = parser.parse_args()
    
    # Setup logger
    logger = LoggerManager.setup_logger('db_cleaner', Config.get_log_path())
    
    # Initialize database manager
    db_path = Config.get_db_path()
    db_manager = DatabaseManager(db_path)
    
    print(f"Database: {db_path}")
    
    if args.action == 'stats':
        # Show database statistics
        stats = db_manager.get_database_stats()
        
        if not stats:
            print("Could not retrieve database statistics")
            return
        
        print(f"\nDatabase Statistics:")
        print(f"Total Posts: {stats.get('total_posts', 0)}")
        print(f"Total Sessions: {stats.get('total_sessions', 0)}")
        
        if stats.get('posts_by_subreddit'):
            print(f"\nPosts by Subreddit:")
            for subreddit, count in stats['posts_by_subreddit'].items():
                print(f"   r/{subreddit}: {count} posts")
        
        if stats.get('oldest_post'):
            oldest_date = datetime.fromtimestamp(stats['oldest_post']).strftime('%Y-%m-%d %H:%M:%S')
            print(f"\nOldest Post: {oldest_date}")
        
        if stats.get('newest_post'):
            newest_date = datetime.fromtimestamp(stats['newest_post']).strftime('%Y-%m-%d %H:%M:%S')
            print(f"Newest Post: {newest_date}")
    
    elif args.action == 'clean':
        # Clean database
        if not args.force:
            if args.subreddit and args.days:
                confirm = input(f"Remove posts from r/{args.subreddit} older than {args.days} days? (yes/no): ").strip().lower()
            elif args.subreddit:
                confirm = input(f"Remove ALL posts from r/{args.subreddit}? (yes/no): ").strip().lower()
            elif args.days:
                confirm = input(f"Remove ALL posts older than {args.days} days? (yes/no): ").strip().lower()
            else:
                confirm = input("Remove ALL posts from database? (yes/no): ").strip().lower()
            
            if confirm != 'yes':
                print("Operation cancelled")
                return
        
        if db_manager.clean_database(subreddit=args.subreddit, older_than_days=args.days):
            print("Database cleaned successfully!")
        else:
            print("Failed to clean database")
    
    elif args.action == 'reset':
        # Reset database
        if not args.force:
            confirm = input("Reset database (delete ALL data)? (yes/no): ").strip().lower()
            if confirm != 'yes':
                print("Operation cancelled")
                return
        
        if db_manager.reset_database():
            print("Database reset successfully!")
        else:
            print("Failed to reset database")

if __name__ == "__main__":
    main() 