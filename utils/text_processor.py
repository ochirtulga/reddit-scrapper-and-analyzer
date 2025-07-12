#!/usr/bin/env python3
"""
Text processing utilities for Reddit Data Mining System
"""

import re
from typing import List, Set
from collections import Counter
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import Config

class TextProcessor:
    """Text processing utilities for word analysis"""
    
    def __init__(self, stop_words: Set[str] = None, min_word_length: int = None):
        self.stop_words = stop_words or Config.STOP_WORDS
        self.min_word_length = min_word_length or Config.MIN_WORD_LENGTH
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text for analysis
        
        Args:
            text (str): Raw text to clean
            
        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove Reddit-specific patterns
        text = re.sub(r'r/\w+', '', text)  # Remove subreddit references
        text = re.sub(r'u/\w+', '', text)  # Remove user references
        
        # Remove special characters but keep apostrophes for contractions
        text = re.sub(r'[^\w\s\']', ' ', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_words(self, text: str) -> List[str]:
        """
        Extract individual words from text
        
        Args:
            text (str): Cleaned text
            
        Returns:
            List[str]: List of filtered words
        """
        if not text:
            return []
        
        # Split into words
        words = text.split()
        
        # Filter out stop words and short words
        filtered_words = []
        for word in words:
            # Remove apostrophes from beginning/end
            word = word.strip("'")
            
            # Skip if too short, is a number, or is a stop word
            if (len(word) >= self.min_word_length and 
                not word.isdigit() and 
                not word.startswith('http') and
                word not in self.stop_words):
                filtered_words.append(word)
        
        return filtered_words
    
    def get_word_frequencies(self, text: str) -> Counter:
        """
        Get word frequencies from text
        
        Args:
            text (str): Text to analyze
            
        Returns:
            Counter: Word frequency counter
        """
        cleaned_text = self.clean_text(text)
        words = self.extract_words(cleaned_text)
        return Counter(words)
    
    def get_context(self, text: str, word: str, context_length: int = None) -> str:
        """
        Get context around a word
        
        Args:
            text (str): Original text
            word (str): Word to find context for
            context_length (int): Length of context to return
            
        Returns:
            str: Context string
        """
        if not text or not word:
            return ""
        
        context_length = context_length or Config.CONTEXT_LENGTH
        
        # Find word in text (case insensitive)
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        match = pattern.search(text)
        
        if not match:
            return text[:context_length] + "..." if len(text) > context_length else text
        
        start = max(0, match.start() - context_length // 2)
        end = min(len(text), match.end() + context_length // 2)
        
        context = text[start:end]
        if start > 0:
            context = "..." + context
        if end < len(text):
            context = context + "..."
        
        return context 