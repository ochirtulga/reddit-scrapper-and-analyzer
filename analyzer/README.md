# Word Frequency Analyzer

Analyzes word frequencies in scraped Reddit data with text cleaning and context tracking.

## Quick Start

```bash
# Prerequisites: Run Reddit scraper first
cd reddit_scraper
python reddit_auto_scraper.py

# Analyze word frequencies
cd word_analyzer
python run_word_analysis.py
```

## Features

- **Text cleaning** - removes URLs, Reddit patterns, special characters
- **Word filtering** - excludes stop words, short words, numbers
- **Context tracking** - stores sample contexts for each word
- **Multiple sources** - analyzes files, database, or both
- **Rich outputs** - JSON, CSV, and text reports

## Usage Examples

```bash
# Basic analysis
python run_word_analysis.py

# Search for words
python run_word_analysis.py --search "python"

# Word details
python run_word_analysis.py --word-details "machine"

# Custom analysis
python run_word_analysis.py --top-n 100 --data-source database
```

## Output Files

- **JSON**: `data/analyzed/json/word_frequencies_[timestamp].json`
- **CSV**: `data/analyzed/csv/word_frequencies_[timestamp].csv`
- **Reports**: `data/analyzed/reports/word_analysis_report_[timestamp].txt`

## Data Processing

### Text Cleaning
1. Lowercase conversion
2. URL removal
3. Reddit pattern removal (`r/subreddit`, `u/username`)
4. Special character removal (keeps apostrophes)
5. Whitespace normalization

### Word Filtering
- **Minimum length**: 3+ characters
- **Stop words**: Common words like "the", "and", "is"
- **Numbers**: Excludes pure numeric strings
- **URLs**: Excludes http/https patterns

### Context Tracking
- **Frequency**: Total occurrences
- **Contexts**: Sample text where word appears
- **Sources**: Number of unique posts containing word

## Sample Output

```
🏆 Top 10 Most Common Words:
 1. python                   45 times
 2. data                     38 times
 3. learning                 32 times
 4. code                     28 times
 5. project                  25 times

✅ Analysis Complete!
📈 Total unique words: 1,250
📊 Total word occurrences: 15,420
```

## Configuration

### Custom Stop Words
```python
# In word_frequency_analyzer.py
self.stop_words = {
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have',
    # Add custom stop words here
}
```

### Output Directories
- `data/analyzed/json/` - JSON format results
- `data/analyzed/csv/` - CSV format results
- `data/analyzed/reports/` - Text reports 