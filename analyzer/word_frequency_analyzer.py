import os
from typing import Dict, List, Tuple, Optional
from ..utils.config import Config
from ..utils.database import DatabaseManager
from ..utils.logger import LoggerManager
from ..utils.text_processor import TextProcessor
from .data_loader import DataLoader
from .word_analyzer import WordAnalyzer
from datetime import datetime

class WordFrequencyAnalyzer:
    """Main analyzer class that orchestrates the analysis process"""
    LAST_ANALYSIS_FILE = os.path.join('data', 'analyzed', 'last_analysis_timestamp.txt')

    def __init__(self):
        self.log_path = Config.get_log_path( Config.DEFAULT_ANALYZER_LOG, "analyzer")
        self.logger = LoggerManager.setup_logger('word_analyzer', self.log_path)
        self.db_manager = DatabaseManager()
        self.text_processor = TextProcessor()
        self.data_loader = DataLoader(self.db_manager)
        self.word_analyzer = WordAnalyzer(self.text_processor)

    def get_last_analysis_timestamp(self) -> Optional[float]:
        try:
            if os.path.exists(self.LAST_ANALYSIS_FILE):
                with open(self.LAST_ANALYSIS_FILE, 'r') as f:
                    ts = f.read().strip()
                    return float(ts)
        except Exception as e:
            self.logger.warning(f"Could not read last analysis timestamp: {e}")
        return None

    def set_last_analysis_timestamp(self, timestamp: float):
        try:
            with open(self.LAST_ANALYSIS_FILE, 'w') as f:
                f.write(str(timestamp))
        except Exception as e:
            self.logger.warning(f"Could not write last analysis timestamp: {e}")

    def analyze_word_frequencies(self, data_source: str = 'database', incremental: bool = False, subreddit: str = None) -> Dict[str, int]:
        self.logger.info("Starting word frequency analysis...")
        all_posts = self.data_loader.load_data_from_database()
        self.logger.info(f"Loaded {len(all_posts)} posts from database")
        if not all_posts:
            self.logger.warning("No posts found to analyze")
            return {}
        unique_posts = {}
        for post in all_posts:
            post_id = post.get('post_id', str(hash(str(post))))
            if post_id not in unique_posts:
                unique_posts[post_id] = post
        all_posts = list(unique_posts.values())
        self.logger.info(f"Processing {len(all_posts)} unique posts")
        if subreddit:
            all_posts = [p for p in all_posts if p.get('subreddit') == subreddit]
        if incremental:
            last_ts = self.get_last_analysis_timestamp()
            if last_ts:
                filtered_posts = []
                for post in all_posts:
                    scraped_at = post.get('scraped_at')
                    if scraped_at:
                        try:
                            scraped_time = datetime.fromisoformat(scraped_at).timestamp()
                            if scraped_time > last_ts:
                                filtered_posts.append(post)
                        except Exception:
                            continue
                all_posts = filtered_posts
                self.logger.info(f"Incremental mode: {len(all_posts)} posts after last analysis at {last_ts}")
            else:
                self.logger.info("Incremental mode: No previous analysis timestamp found, analyzing all posts.")
        frequencies = self.word_analyzer.analyze_posts(all_posts)
        self.logger.info(f"Analysis complete. Found {len(frequencies)} unique words")
        if all_posts:
            scraped_times = [
                datetime.fromisoformat(p['scraped_at']).timestamp()
                for p in all_posts if p.get('scraped_at')
            ]
            if scraped_times:
                latest_scraped = max(scraped_times)
                self.set_last_analysis_timestamp(latest_scraped)
        if subreddit:
            self.db_manager.save_word_frequencies(self.word_analyzer.word_frequencies, subreddit)
        else:
            # Save for all subreddits
            subreddits = set(p.get('subreddit') for p in all_posts)
            for sub in subreddits:
                sub_freqs = {w: c for w, c in self.word_analyzer.word_frequencies.items()}
                self.db_manager.save_word_frequencies(sub_freqs, sub)
        return frequencies

    def get_word_details(self, word: str) -> Dict:
        return self.word_analyzer.get_word_details(word)

    def search_words(self, pattern: str) -> List[Tuple[str, int]]:
        return self.word_analyzer.search_words(pattern)

    def get_top_words(self, top_n: int = 10, subreddit: str = None) -> List[Dict[str, int]]:
        return self.db_manager.get_top_words(top_n=top_n, subreddit=subreddit) 