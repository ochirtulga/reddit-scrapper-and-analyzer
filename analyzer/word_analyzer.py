import re
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Optional
from ..utils.text_processor import TextProcessor

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
        text_fields = ['title']
        if post_data.get('is_self', False) and 'selftext' in post_data:
            text_fields.append('selftext')
        for field in text_fields:
            if field in post_data and post_data[field]:
                text = post_data[field]
                word_freqs = self.text_processor.get_word_frequencies(text)
                for word, count in word_freqs.items():
                    post_words[word] += count
                    context = self.text_processor.get_context(text, word)
                    if context:
                        self.word_contexts[word].append(context)
                    if post_id:
                        self.word_sources[word].add(post_id)
        return dict(post_words)
    
    def analyze_posts(self, posts: List[Dict]) -> Dict[str, int]:
        self.word_frequencies.clear()
        self.word_contexts.clear()
        self.word_sources.clear()
        for post in posts:
            post_id = post.get('post_id', str(hash(str(post))))
            post_words = self.process_post_data(post, post_id)
            for word, count in post_words.items():
                self.word_frequencies[word] += count
        return dict(self.word_frequencies)
    
    def get_word_details(self, word: str) -> Dict:
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
        matches = []
        try:
            regex = re.compile(pattern, re.IGNORECASE)
            for word in self.word_frequencies:
                if regex.search(word):
                    matches.append((word, self.word_frequencies[word]))
            matches.sort(key=lambda x: x[1], reverse=True)
        except re.error as e:
            print(f"Invalid regex pattern: {e}")
        return matches 