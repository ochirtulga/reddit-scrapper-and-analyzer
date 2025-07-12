# Reddit Data Mining & Word Analysis

Automated Reddit scraping and word frequency analysis system.

## Quick Start

```bash
# Install dependencies
pip install requests beautifulsoup4

# Scrape Reddit data
cd scraper
python scraper.py

# Analyze word frequencies
cd analyzer
python run.py
```

## Project Structure

```
reddit-scrapper-and-analyzer/
├── scraper/                 # Reddit data collection
├── analyzer/                # Word frequency analysis
├── data/                    # All data storage
│   ├── scraped/            # Raw scraped data (CSV/JSON)
│   ├── analyzed/           # Processed analysis data
│   ├── db/                 # SQLite database
│   └── logs/               # Log files
└── README.md
```

## Features

### Reddit Scraper
- Automated scraping at configurable intervals (default: 60 min)
- Incremental updates (only new posts)
- SQLite database tracking
- JSON/CSV output formats

### Word Analyzer
- Text cleaning and word filtering
- Multiple data sources (files/database)
- Context tracking and source analysis
- JSON/CSV/Text report outputs

## Usage Examples

```bash
# Scrape r/Python every 30 minutes
cd scraper
python scraper.py
# Enter: Python, 30, data

# Analyze word frequencies
cd analyzer
python run.py

# Search for specific words
python run.py --search "python"

# Get word details
python run.py --word-details "machine"

# Database management
python3 manage_database.py
python3 clean_db.py stats
```

## Output Files

- **Scraped**: `data/scraped/{csv,json}/reddit_auto_[subreddit]_[timestamp].{csv,json}`
- **Analyzed**: `data/analyzed/{csv,json}/word_frequencies_[timestamp].{csv,json}`
- **Reports**: `data/analyzed/reports/word_analysis_report_[timestamp].txt`
- **Database**: `data/db/reddit_scraper.db`
- **Logs**: `data/logs/{reddit_scraper,word_analyzer}.log`

## Configuration

- **Subreddit**: Configurable (default: Python)
- **Interval**: Configurable in minutes (default: 60)
- **Output**: Customizable directories
- **Data sources**: Files, database, or both 