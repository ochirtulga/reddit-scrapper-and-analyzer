#!/usr/bin/env python3
"""
Simple script to run word frequency analysis on Reddit scraped data
"""

from analyzer import WordFrequencyAnalyzer
import argparse

def main():
    parser = argparse.ArgumentParser(description='Analyze word frequencies in Reddit scraped data')
    parser.add_argument('--data-source', choices=['files', 'database', 'both'], default='both',
                       help='Source of data to analyze (default: both)')
    parser.add_argument('--output-dir', default='data/analyzed',
                       help='Output directory for analysis results (default: data/analyzed)')
    parser.add_argument('--top-n', type=int, default=50,
                       help='Number of top words to show in report (default: 50)')
    parser.add_argument('--search', type=str,
                       help='Search for words matching a regex pattern')
    parser.add_argument('--word-details', type=str,
                       help='Get detailed information about a specific word')
    parser.add_argument('--incremental', action='store_true',
                       help='Only analyze newly scraped data since last analysis')
    
    args = parser.parse_args()
    
    print("🔍 Reddit Word Frequency Analyzer")
    print("=" * 40)
    
    # Initialize analyzer
    analyzer = WordFrequencyAnalyzer(output_dir=args.output_dir)
    
    # Analyze word frequencies
    print(f"\nAnalyzing word frequencies from {args.data_source}...{' (incremental mode)' if args.incremental else ''}")
    frequencies = analyzer.analyze_word_frequencies(data_source=args.data_source, incremental=args.incremental)
    
    if not frequencies:
        print("❌ No data found to analyze. Make sure you have scraped some Reddit data first.")
        print("\n💡 To scrape Reddit data, run:")
        print("   python reddit_auto_scraper.py")
        return
    
    # Handle specific word search
    if args.search:
        print(f"\n🔍 Searching for words matching pattern: {args.search}")
        matches = analyzer.search_words(args.search)
        if matches:
            print(f"Found {len(matches)} matching words:")
            for word, count in matches[:20]:  # Show top 20
                print(f"  {word:<20} {count:>6} times")
        else:
            print("No words found matching the pattern.")
        return
    
    # Handle specific word details
    if args.word_details:
        print(f"\n📋 Details for word: {args.word_details}")
        details = analyzer.get_word_details(args.word_details.lower())
        if details:
            print(f"Word: {details['word']}")
            print(f"Frequency: {details['frequency']} times")
            print(f"Appears in: {details['sources_count']} posts")
            print(f"Sample contexts:")
            for i, context in enumerate(details['contexts'][:5], 1):
                print(f"  {i}. {context}")
        else:
            print(f"Word '{args.word_details}' not found in the data.")
        return
    
    # Save results
    print("\n💾 Saving word frequency data...")
    json_file, csv_file = analyzer.save_word_frequencies()
    
    # Generate report
    print(f"\n📋 Generating analysis report (top {args.top_n} words)...")
    report_file = analyzer.generate_report(top_n=args.top_n)
    
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
    print(f"   - All analyzed data: data/analyzed/")
    
    print(f"\nAdditional commands you can try:")
    print(f"   python run.py --search 'python'")
    print(f"   python run.py --word-details 'python'")
    print(f"   python run.py --data-source database --top-n 100")

if __name__ == "__main__":
    main() 