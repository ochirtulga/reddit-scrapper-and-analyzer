#!/usr/bin/env python3
"""
Word Frequency Analyzer - CLI entry point
"""
from .word_frequency_analyzer import WordFrequencyAnalyzer

def main():
    """Main function to run word frequency analysis"""
    analyzer = WordFrequencyAnalyzer()
    print("Reddit Word Frequency Analyzer")
    print("=" * 40)
    print("\n Analyzing word frequencies...")
    frequencies = analyzer.analyze_word_frequencies(data_source='database')
    if not frequencies:
        print("No data found to analyze. Make sure you have scraped some Reddit data first.")
        return
    print(f"\n Top 10 Most Common Words:")
    print("-" * 40)
    for i, (word, count) in enumerate(analyzer.word_analyzer.word_frequencies.most_common(10), 1):
        print(f"{i:2d}. {word:<20} {count:>6} times")

if __name__ == "__main__":
    main()