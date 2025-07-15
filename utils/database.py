#!/usr/bin/env python3
"""
Database utilities for Reddit Data Mining System
"""

import logging
from typing import Counter, Optional, List, Dict, Any
from contextlib import contextmanager
from .config import Config
import sys
import os
import psycopg2

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class DatabaseManager:
    """Database manager for handling SQLite and PostgreSQL operations"""
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.db_type = Config.DB_TYPE

    @contextmanager
    def get_connection(self):
        """Context manager for database connections (SQLite or PostgreSQL)"""
        conn = None
        try:
            conn = psycopg2.connect(
                host=Config.POSTGRES_HOST,
                port=Config.POSTGRES_PORT,
                dbname=Config.POSTGRES_DB,
                user=Config.POSTGRES_USER,
                password=Config.POSTGRES_PASSWORD
            )
            yield conn
        except Exception as e:
            self.logger.error(f"Database connection error: {e}")
            if conn:
                if self.db_type == 'sqlite':
                    conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    def init_database(self) -> bool:
        """Initialize database with required tables"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                tables = Config.get_database_tables()
                for table_name, create_sql in tables.items():
                    cursor.execute(create_sql)
                    self.logger.info(f"Created table: {table_name}")
                conn.commit()
                return True
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
            return False
    
    def clean_database(self, subreddit: Optional[str] = None, older_than_days: Optional[int] = None) -> bool:
        """
        Clean the database by removing old data
        
        Args:
            subreddit (str, optional): Only clean data from specific subreddit
            older_than_days (int, optional): Remove posts older than X days
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Build WHERE clause
                where_conditions = []
                params = []
                
                if subreddit:
                    where_conditions.append("subreddit = ?")
                    params.append(subreddit)
                
                if older_than_days:
                    import time
                    cutoff_time = time.time() - (older_than_days * 24 * 60 * 60)
                    where_conditions.append("created_utc < ?")
                    params.append(cutoff_time)
                
                where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
                
                # Get count before deletion
                count_query = f"SELECT COUNT(*) FROM scraped_posts WHERE {where_clause}"
                cursor.execute(count_query, params)
                count_before = cursor.fetchone()[0]
                
                # Delete posts
                delete_query = f"DELETE FROM scraped_posts WHERE {where_clause}"
                cursor.execute(delete_query, params)
                
                # Clean up orphaned sessions
                if subreddit:
                    cursor.execute("DELETE FROM scraping_sessions WHERE subreddit = ?", (subreddit,))
                elif older_than_days:
                    import time
                    cutoff_time = time.time() - (older_than_days * 24 * 60 * 60)
                    cursor.execute("DELETE FROM scraping_sessions WHERE session_start < ?", 
                                 (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cutoff_time)),))
                
                conn.commit()
                
                self.logger.info(f"Database cleaned: {count_before} posts removed")
                return True
                
        except Exception as e:
            self.logger.error(f"Error cleaning database: {e}")
            return False
    
    def reset_database(self) -> bool:
        """
        Reset the database by dropping all tables and recreating them
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Drop existing tables
                cursor.execute("DROP TABLE IF EXISTS scraped_posts")
                cursor.execute("DROP TABLE IF EXISTS scraping_sessions")
                cursor.execute("DROP TABLE IF EXISTS word_frequencies")
                
                # Recreate tables
                tables = Config.get_database_tables()
                for table_name, create_sql in tables.items():
                    cursor.execute(create_sql)
                    self.logger.info(f"Recreated table: {table_name}")
                
                conn.commit()
                self.logger.info("Database reset completed")
                return True
                
        except Exception as e:
            self.logger.error(f"Error resetting database: {e}")
            return False
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics
        
        Returns:
            Dict with database statistics
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get total posts
                cursor.execute("SELECT COUNT(*) FROM scraped_posts")
                total_posts = cursor.fetchone()[0]
                
                # Get posts by subreddit
                cursor.execute("SELECT subreddit, COUNT(*) FROM scraped_posts GROUP BY subreddit")
                posts_by_subreddit = dict(cursor.fetchall())
                
                # Get total sessions
                cursor.execute("SELECT COUNT(*) FROM scraping_sessions")
                total_sessions = cursor.fetchone()[0]
                
                # Get oldest and newest posts
                cursor.execute("SELECT MIN(created_utc), MAX(created_utc) FROM scraped_posts")
                oldest_newest = cursor.fetchone()
                oldest_post = oldest_newest[0] if oldest_newest[0] else None
                newest_post = oldest_newest[1] if oldest_newest[1] else None
                
                return {
                    'total_posts': total_posts,
                    'posts_by_subreddit': posts_by_subreddit,
                    'total_sessions': total_sessions,
                    'oldest_post': oldest_post,
                    'newest_post': newest_post
                }
                
        except Exception as e:
            self.logger.error(f"Error getting database stats: {e}")
            return {}
    
    def execute_query(self, query: str, params: tuple = ()) -> Optional[List[tuple]]:
        """Execute a query and return results"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query.replace('?', '%s'), params)
                return cursor.fetchall()
        except Exception as e:
            self.logger.error(f"Query execution error: {e}")
            return None
    
    def execute_update(self, query: str, params: tuple = ()) -> bool:
        """Execute an update/insert query"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query.replace('?', '%s'), params)
                conn.commit()
                return True
        except Exception as e:
            self.logger.error(f"Update execution error: {e}")
            return False
    
    def get_last_timestamp(self, subreddit: str) -> Optional[float]:
        """Get the timestamp of the last scraped post for a subreddit"""
        query = '''
            SELECT MAX(created_utc) FROM scraped_posts 
            WHERE subreddit = ?
        '''
        result = self.execute_query(query, (subreddit,))
        return result[0][0] if result and result[0] and result[0][0] else None
    
    def post_exists(self, post_id: str) -> bool:
        """Check if a post already exists in the database"""
        query = 'SELECT 1 FROM scraped_posts WHERE post_id = ?'
        result = self.execute_query(query, (post_id,))
        return bool(result)
    
    def save_post(self, post_data: Dict[str, Any]) -> bool:
        """Save a post to the database (upsert)"""
        query = '''
            INSERT INTO scraped_posts (post_id, title, author, score, num_comments, created_utc, scraped_at, subreddit, url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (post_id) DO UPDATE SET
                title = EXCLUDED.title,
                author = EXCLUDED.author,
                score = EXCLUDED.score,
                num_comments = EXCLUDED.num_comments,
                created_utc = EXCLUDED.created_utc,
                scraped_at = EXCLUDED.scraped_at,
                subreddit = EXCLUDED.subreddit,
                url = EXCLUDED.url
        '''
        params = (
            post_data['post_id'],
            post_data['title'],
            post_data['author'],
            post_data['score'],
            post_data['num_comments'],
            post_data['created_utc'],
            post_data['scraped_at'],
            post_data['subreddit'],
            post_data.get('url', None)
        )
        return self.execute_update(query, params)
    
    def save_session(self, session_start: str, posts_scraped: int, subreddit: str) -> bool:
        """Save a scraping session to the database"""
        query = '''
            INSERT INTO scraping_sessions 
            (session_start, session_end, posts_scraped, subreddit)
            VALUES (?, ?, ?, ?)
        '''
        from datetime import datetime
        session_end = datetime.now().isoformat()
        params = (session_start, session_end, posts_scraped, subreddit)
        return self.execute_update(query, params)
    
    def get_posts_for_analysis(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get posts for word analysis"""
        query = '''
            SELECT post_id, title, author, score, num_comments, created_utc, scraped_at, subreddit, url
            FROM scraped_posts
            ORDER BY created_utc DESC
        '''
        if limit:
            query += f' LIMIT {limit}'
        
        result = self.execute_query(query)
        if not result:
            return []
        
        return [
            {
                'post_id': row[0],
                'title': row[1],
                'author': row[2],
                'score': row[3],
                'num_comments': row[4],
                'created_utc': row[5],
                'scraped_at': row[6],
                'subreddit': row[7],
                'url': row[8]
            }
            for row in result
        ] 

    def save_word_frequencies(self, word_frequencies: Counter, subreddit: str):
        """Upsert word frequencies into the database for a specific subreddit"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for word, freq in word_frequencies.items():
                query = """
                    INSERT INTO word_frequencies (word, subreddit, frequency)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (word, subreddit) DO UPDATE SET frequency = EXCLUDED.frequency
                """
                cursor.execute(query, (word, subreddit, freq))
            conn.commit()

    def update_word_frequencies(self, new_word_frequencies: Dict[str, int], subreddit: str):
        """Increment word frequencies for new posts (additive update) for a specific subreddit"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for word, freq in new_word_frequencies.items():
                query = """
                    INSERT INTO word_frequencies (word, subreddit, frequency)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (word, subreddit) DO UPDATE SET frequency = word_frequencies.frequency + EXCLUDED.frequency
                """
                cursor.execute(query, (word, subreddit, freq))
            conn.commit()

    def get_top_words(self, top_n: int = 10, subreddit: str = None) -> List[Dict[str, int]]:
        """Get top words, optionally filtered by subreddit"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if subreddit:
                query = """
                    SELECT word, frequency FROM word_frequencies
                    WHERE subreddit = %s
                    ORDER BY frequency DESC
                    LIMIT %s
                """
                cursor.execute(query, (subreddit, top_n))
            else:
                query = """
                    SELECT word, SUM(frequency) as frequency FROM word_frequencies
                    GROUP BY word
                    ORDER BY frequency DESC
                    LIMIT %s
                """
                cursor.execute(query, (top_n,))
            results = cursor.fetchall()
            return [{"word": row[0], "frequency": row[1]} for row in results] 

    def list_subreddits(self) -> List[str]:
        """List all subreddits present in the word_frequencies table"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT subreddit FROM word_frequencies ORDER BY subreddit ASC")
            results = cursor.fetchall()
            return [row[0] for row in results] 

    def add_scraped_subreddit(self, subreddit: str):
        """Insert a subreddit into scraped_subreddits if not already present"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO scraped_subreddits (subreddit)
                VALUES (%s)
                ON CONFLICT (subreddit) DO NOTHING
                """,
                (subreddit,)
            )
            conn.commit()

    def list_scraped_subreddits(self) -> list:
        """List all subreddits from scraped_subreddits table"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT subreddit FROM scraped_subreddits ORDER BY subreddit ASC")
            results = cursor.fetchall()
            return [row[0] for row in results] 