#!/usr/bin/env python3
"""
Database Management Tool for Reddit Data Mining System
Allows cleaning, resetting, and viewing database statistics
"""

import sys
import os
from datetime import datetime
import time

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.config import Config
from utils.database import DatabaseManager
from utils.logger import LoggerManager

def print_banner():
    """Print the tool banner"""
    print("=" * 60)
    print("Reddit Database Management Tool")
    print("=" * 60)

def show_database_stats(db_manager: DatabaseManager):
    """Show database statistics"""
    print("\nDatabase Statistics:")
    print("-" * 30)
    
    stats = db_manager.get_database_stats()
    
    if not stats:
        print("Could not retrieve database statistics")
        return
    
    print(f"Total Posts: {stats.get('total_posts', 0)}")
    print(f"Total Sessions: {stats.get('total_sessions', 0)}")
    
    if stats.get('posts_by_subreddit'):
        print("\nPosts by Subreddit:")
        for subreddit, count in stats['posts_by_subreddit'].items():
            print(f"   r/{subreddit}: {count} posts")
    
    if stats.get('oldest_post'):
        oldest_date = datetime.fromtimestamp(stats['oldest_post']).strftime('%Y-%m-%d %H:%M:%S')
        print(f"\nOldest Post: {oldest_date}")
    
    if stats.get('newest_post'):
        newest_date = datetime.fromtimestamp(stats['newest_post']).strftime('%Y-%m-%d %H:%M:%S')
        print(f"Newest Post: {newest_date}")

def clean_database_menu(db_manager: DatabaseManager):
    """Show database cleaning options"""
    print("\nDatabase Cleaning Options:")
    print("-" * 30)
    print("1. Clean all data")
    print("2. Clean data from specific subreddit")
    print("3. Clean data older than X days")
    print("4. Clean data from specific subreddit older than X days")
    print("5. Back to main menu")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    if choice == "1":
        confirm = input("This will delete ALL posts. Are you sure? (yes/no): ").strip().lower()
        if confirm == "yes":
            if db_manager.clean_database():
                print("Database cleaned successfully!")
            else:
                print("Failed to clean database")
        else:
            print("Operation cancelled")
    
    elif choice == "2":
        subreddit = input("Enter subreddit name (without r/): ").strip()
        if subreddit:
            confirm = input(f"This will delete ALL posts from r/{subreddit}. Are you sure? (yes/no): ").strip().lower()
            if confirm == "yes":
                if db_manager.clean_database(subreddit=subreddit):
                    print(f"Database cleaned for r/{subreddit}!")
                else:
                    print("Failed to clean database")
            else:
                print("Operation cancelled")
        else:
            print("Invalid subreddit name")
    
    elif choice == "3":
        try:
            days = int(input("Enter number of days (posts older than this will be deleted): ").strip())
            if days > 0:
                confirm = input(f"This will delete posts older than {days} days. Are you sure? (yes/no): ").strip().lower()
                if confirm == "yes":
                    if db_manager.clean_database(older_than_days=days):
                        print(f"Database cleaned! Posts older than {days} days removed.")
                    else:
                        print("Failed to clean database")
                else:
                    print("Operation cancelled")
            else:
                print("Invalid number of days")
        except ValueError:
            print("Please enter a valid number")
    
    elif choice == "4":
        subreddit = input("Enter subreddit name (without r/): ").strip()
        if subreddit:
            try:
                days = int(input("Enter number of days (posts older than this will be deleted): ").strip())
                if days > 0:
                    confirm = input(f"This will delete posts from r/{subreddit} older than {days} days. Are you sure? (yes/no): ").strip().lower()
                    if confirm == "yes":
                        if db_manager.clean_database(subreddit=subreddit, older_than_days=days):
                            print(f"Database cleaned for r/{subreddit}! Posts older than {days} days removed.")
                        else:
                            print("Failed to clean database")
                    else:
                        print("Operation cancelled")
                else:
                    print("Invalid number of days")
            except ValueError:
                print("Please enter a valid number")
        else:
            print("Invalid subreddit name")
    
    elif choice == "5":
        return
    
    else:
        print("Invalid option")

def reset_database_menu(db_manager: DatabaseManager):
    """Show database reset options"""
    print("\nDatabase Reset:")
    print("-" * 20)
    print("WARNING: This will delete ALL data and recreate empty tables!")
    
    confirm = input("Are you absolutely sure you want to reset the database? (yes/no): ").strip().lower()
    
    if confirm == "yes":
        double_confirm = input("Type 'RESET' to confirm: ").strip()
        if double_confirm == "RESET":
            if db_manager.reset_database():
                print("Database reset successfully!")
            else:
                print("Failed to reset database")
        else:
            print("Reset cancelled")
    else:
        print("Reset cancelled")

def main():
    """Main function"""
    print_banner()
    
    # Setup logger
    logger = LoggerManager.setup_logger('db_manager', Config.get_log_path())
    
    # Initialize database manager
    db_path = Config.get_db_path()
    db_manager = DatabaseManager(db_path)
    
    print(f"Database: {db_path}")
    
    while True:
        print("\n" + "=" * 60)
        print("Main Menu:")
        print("1. Show Database Statistics")
        print("2. Clean Database")
        print("3. Reset Database")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            show_database_stats(db_manager)
        
        elif choice == "2":
            clean_database_menu(db_manager)
        
        elif choice == "3":
            reset_database_menu(db_manager)
        
        elif choice == "4":
            print("\nGoodbye!")
            break
        
        else:
            print("Invalid option. Please select 1-4.")

if __name__ == "__main__":
    main() 