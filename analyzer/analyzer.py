 #!/usr/bin/env python3
"""
Word Frequency Analyzer
"""

import re
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Set, Tuple, Optional
import sys
import os
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import Config
from utils.database import DatabaseManager
from utils.file_manager import FileManager
from utils.logger import LoggerManager
from utils.text_processor import TextProcessor

class DataLoader:
    """Handles data loading from multiple sources (Single Responsibility)"""
    
    def __init__(self, file_manager: FileManager, db_manager: DatabaseManager):
        self.file_manager = file_manager
        self.db_manager = db_manager
    
    def load_data_from_files(self) -> List[Dict]:
        """Load all scraped data from JSON and CSV files"""
        all_posts = []
        
        # Load from JSON files
        json_files = self.file_manager.list_files('json', '.json')
        for filename in json_files:
            try:
                posts = self.file_manager.load_json_data(filename, 'json')
                all_posts.extend(posts)
            except Exception as e:
                print(f"Error loading {filename}: {e}")
        
        # Load from CSV files
        csv_files = self.file_manager.list_files('csv', '.csv')
        for filename in csv_files:
            try:
                posts = self.file_manager.load_csv_data(filename, 'csv')
                all_posts.extend(posts)
            except Exception as e:
                print(f"Error loading {filename}: {e}")
        
        return all_posts
    
    def load_data_from_database(self) -> List[Dict]:
        """Load all scraped data from SQLite database"""
        return self.db_manager.get_posts_for_analysis()

class WordAnalyzer:
    """Handles word analysis logic (Single Responsibility)"""
    
    def __init__(self, text_processor: TextProcessor):
        self.text_processor = text_processor
        self.word_frequencies = Counter()
        self.word_contexts = defaultdict(list)
        self.word_sources = defaultdict(set)
    
    def process_post_data(self, post_data: Dict, post_id: Optional[str] = None) -> Dict[str, int]:
        """Process a single post and extract word frequencies"""
        post_words = Counter()
        
        # Extract text from relevant fields
        text_fields = ['title']
        
        # Add selftext if available (for text posts)
        if post_data.get('is_self', False) and 'selftext' in post_data:
            text_fields.append('selftext')
        
        for field in text_fields:
            if field in post_data and post_data[field]:
                text = post_data[field]
                word_freqs = self.text_processor.get_word_frequencies(text)
                
                # Count words in this post
                for word, count in word_freqs.items():
                    post_words[word] += count
                    
                    # Store context
                    context = self.text_processor.get_context(text, word)
                    if context:
                        self.word_contexts[word].append(context)
                    
                    # Track source post
                    if post_id:
                        self.word_sources[word].add(post_id)
        
        return dict(post_words)
    
    def analyze_posts(self, posts: List[Dict]) -> Dict[str, int]:
        """Analyze word frequencies from posts"""
        # Clear previous analysis
        self.word_frequencies.clear()
        self.word_contexts.clear()
        self.word_sources.clear()
        
        # Process each post
        for post in posts:
            post_id = post.get('post_id', str(hash(str(post))))
            post_words = self.process_post_data(post, post_id)
            
            # Add to global word frequencies
            for word, count in post_words.items():
                self.word_frequencies[word] += count
        
        return dict(self.word_frequencies)
    
    def get_word_details(self, word: str) -> Dict:
        """Get detailed information about a specific word"""
        if word not in self.word_frequencies:
            return {}
        
        return {
            'word': word,
            'frequency': self.word_frequencies[word],
            'contexts': self.word_contexts.get(word, []),
            'sources_count': len(self.word_sources.get(word, set())),
            'sources': list(self.word_sources.get(word, set()))
        }
    
    def search_words(self, pattern: str) -> List[Tuple[str, int]]:
        """Search for words matching a pattern"""
        matches = []
        
        try:
            regex = re.compile(pattern, re.IGNORECASE)
            for word in self.word_frequencies:
                if regex.search(word):
                    matches.append((word, self.word_frequencies[word]))
            
            # Sort by frequency
            matches.sort(key=lambda x: x[1], reverse=True)
            
        except re.error as e:
            print(f"Invalid regex pattern: {e}")
        
        return matches

class ReportGenerator:
    """Handles report generation (Single Responsibility)"""
    
    def __init__(self, file_manager: FileManager):
        self.file_manager = file_manager
    
    def generate_report(self, word_frequencies: Counter, word_contexts: Dict, 
                       word_sources: Dict, top_n: int = None) -> str:
        """Generate a comprehensive analysis report"""
        top_n = top_n or Config.DEFAULT_TOP_N
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        report_content = []
        report_content.append("=" * 60)
        report_content.append("WORD FREQUENCY ANALYSIS REPORT")
        report_content.append("=" * 60)
        report_content.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_content.append(f"Data Source: Reddit Scraper")
        report_content.append(f"Total Unique Words: {len(word_frequencies):,}")
        report_content.append(f"Total Word Occurrences: {sum(word_frequencies.values()):,}")
        report_content.append("")
        
        # Top words by frequency
        report_content.append("TOP WORDS BY FREQUENCY:")
        report_content.append("-" * 40)
        for i, (word, count) in enumerate(word_frequencies.most_common(top_n), 1):
            sources = len(word_sources.get(word, set()))
            report_content.append(f"{i:2d}. {word:<20} {count:>6} times (in {sources} posts)")
        
        # Most common word patterns
        report_content.append("")
        report_content.append("MOST COMMON WORD PATTERNS:")
        report_content.append("-" * 40)
        pattern_stats = defaultdict(int)
        for word in word_frequencies:
            if len(word) >= 4:
                pattern = word[:4] + "*"
                pattern_stats[pattern] += word_frequencies[word]
        
        for pattern, count in sorted(pattern_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
            report_content.append(f"{pattern}: {count:,} occurrences")
        
        report_content = "\n".join(report_content)
        
        # Save report
        filename = f"word_analysis_report_{timestamp}.txt"
        return self.file_manager.save_report(report_content, filename)

class WordFrequencyAnalyzer:
    """Main analyzer class that orchestrates the analysis process"""
    
    LAST_ANALYSIS_FILE = os.path.join('data', 'analyzed', 'last_analysis_timestamp.txt')

    def __init__(self, data_dir: str = None, output_dir: str = None, db_path: str = None):
        """
        Initialize the word frequency analyzer
        
        Args:
            data_dir (str): Directory containing scraped data
            output_dir (str): Directory to save word analysis results
            db_path (str): SQLite database path for scraped posts
        """
        self.data_dir = data_dir or Config.DEFAULT_DATA_DIR
        self.output_dir = output_dir or Config.DEFAULT_OUTPUT_DIR
        
        # Initialize components
        self.db_path = db_path or Config.get_db_path(self.data_dir)
        self.log_path = Config.get_log_path(self.data_dir, Config.DEFAULT_ANALYZER_LOG)
        
        # Setup utilities
        self.logger = LoggerManager.setup_logger('word_analyzer', self.log_path)
        self.db_manager = DatabaseManager(self.db_path)
        self.file_manager = FileManager(self.data_dir)
        self.text_processor = TextProcessor()
        
        # Initialize components
        self.data_loader = DataLoader(self.file_manager, self.db_manager)
        self.word_analyzer = WordAnalyzer(self.text_processor)
        self.report_generator = ReportGenerator(self.file_manager)
    
    def get_last_analysis_timestamp(self) -> Optional[float]:
        """Read the last analysis timestamp from file"""
        try:
            if os.path.exists(self.LAST_ANALYSIS_FILE):
                with open(self.LAST_ANALYSIS_FILE, 'r') as f:
                    ts = f.read().strip()
                    return float(ts)
        except Exception as e:
            self.logger.warning(f"Could not read last analysis timestamp: {e}")
        return None

    def set_last_analysis_timestamp(self, timestamp: float):
        """Write the last analysis timestamp to file"""
        try:
            with open(self.LAST_ANALYSIS_FILE, 'w') as f:
                f.write(str(timestamp))
        except Exception as e:
            self.logger.warning(f"Could not write last analysis timestamp: {e}")

    def analyze_word_frequencies(self, data_source: str = 'both', incremental: bool = False) -> Dict[str, int]:
        """
        Analyze word frequencies from scraped data
        
        Args:
            data_source (str): Source of data ('files', 'database', or 'both')
            incremental (bool): If True, only analyze posts scraped after the last analysis
            
        Returns:
            Dict[str, int]: Word frequency dictionary
        """
        self.logger.info("Starting word frequency analysis...")
        
        all_posts = []
        
        if data_source in ['files', 'both']:
            file_posts = self.data_loader.load_data_from_files()
            all_posts.extend(file_posts)
            self.logger.info(f"Loaded {len(file_posts)} posts from files")
        
        if data_source in ['database', 'both']:
            db_posts = self.data_loader.load_data_from_database()
            all_posts.extend(db_posts)
            self.logger.info(f"Loaded {len(db_posts)} posts from database")
        
        if not all_posts:
            self.logger.warning("No posts found to analyze")
            return {}
        
        # Remove duplicates based on post_id
        unique_posts = {}
        for post in all_posts:
            post_id = post.get('post_id', str(hash(str(post))))
            if post_id not in unique_posts:
                unique_posts[post_id] = post
        
        all_posts = list(unique_posts.values())
        self.logger.info(f"Processing {len(all_posts)} unique posts")
        
        # Incremental filtering
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
        
        # Analyze word frequencies
        frequencies = self.word_analyzer.analyze_posts(all_posts)
        
        self.logger.info(f"Analysis complete. Found {len(frequencies)} unique words")
        # Update last analysis timestamp
        if all_posts:
            scraped_times = [
                datetime.fromisoformat(p['scraped_at']).timestamp()
                for p in all_posts if p.get('scraped_at')
            ]
            if scraped_times:
                latest_scraped = max(scraped_times)
                self.set_last_analysis_timestamp(latest_scraped)
        return frequencies
    
    def save_word_frequencies(self, filename_prefix: Optional[str] = None) -> Tuple[str, str]:
        """Save word frequency data to files"""
        if not filename_prefix:
            filename_prefix = self.file_manager.get_timestamped_filename("word_frequencies", "")
            if not filename_prefix:
                filename_prefix = "word_frequencies"
            else:
                filename_prefix = filename_prefix[:-1]  # Remove trailing dot
        
        # Prepare data for saving
        word_data = []
        for word, count in self.word_analyzer.word_frequencies.most_common():
            contexts = self.word_analyzer.word_contexts.get(word, [])
            sources_count = len(self.word_analyzer.word_sources.get(word, set()))
            
            word_data.append({
                'word': word,
                'frequency': count,
                'contexts_count': len(contexts),
                'sources_count': sources_count,
                'sample_contexts': contexts[:3],  # First 3 contexts
                'first_seen': min([ctx for ctx in contexts]) if contexts else None
            })
        
        # Save to files
        json_file = self.file_manager.save_json_data(word_data, f"{filename_prefix or ''}.json", 'analyzed')
        csv_file = self.file_manager.save_csv_data(word_data, f"{filename_prefix or ''}.csv", 'analyzed')
        
        self.logger.info(f"Word frequencies saved to {json_file} and {csv_file}")
        return json_file, csv_file
    
    def generate_report(self, top_n: int = None) -> str:
        """Generate a comprehensive analysis report"""
        if top_n is None:
            top_n = Config.DEFAULT_TOP_N
        
        report_file = self.report_generator.generate_report(
            self.word_analyzer.word_frequencies,
            self.word_analyzer.word_contexts,
            self.word_analyzer.word_sources,
            top_n
        )
        
        self.logger.info(f"Analysis report saved to {report_file}")
        return report_file
    
    def get_word_details(self, word: str) -> Dict:
        """Get detailed information about a specific word"""
        return self.word_analyzer.get_word_details(word)
    
    def search_words(self, pattern: str) -> List[Tuple[str, int]]:
        """Search for words matching a pattern"""
        return self.word_analyzer.search_words(pattern)

def main():
    """Main function to run word frequency analysis"""
    analyzer = WordFrequencyAnalyzer()
    
    print("🔍 Reddit Word Frequency Analyzer")
    print("=" * 40)
    
    # Analyze word frequencies
    print("\n📊 Analyzing word frequencies...")
    frequencies = analyzer.analyze_word_frequencies(data_source='both')
    
    if not frequencies:
        print("❌ No data found to analyze. Make sure you have scraped some Reddit data first.")
        return
    
    # Save results
    print("\n💾 Saving word frequency data...")
    json_file, csv_file = analyzer.save_word_frequencies()
    
    # Generate report
    print("\n📋 Generating analysis report...")
    report_file = analyzer.generate_report(top_n=50)
    
    # Display summary
    print(f"\n✅ Analysis Complete!")
    print(f"📈 Total unique words: {len(frequencies):,}")
    print(f"📊 Total word occurrences: {sum(frequencies.values()):,}")
    print(f"📁 Results saved to: {analyzer.output_dir}/")
    print(f"📄 Report: {report_file}")
    
    # Show top words
    print(f"\n🏆 Top 10 Most Common Words:")
    print("-" * 40)
    for i, (word, count) in enumerate(analyzer.word_analyzer.word_frequencies.most_common(10), 1):
        print(f"{i:2d}. {word:<20} {count:>6} times")
    
    print(f"\n🎯 You can now explore the word frequency data in:")
    print(f"   - JSON format: {json_file}")
    print(f"   - CSV format: {csv_file}")
    print(f"   - Detailed report: {report_file}")

if __name__ == "__main__":
    main()