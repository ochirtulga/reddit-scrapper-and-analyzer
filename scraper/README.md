# Reddit Auto Scraper

Automated Reddit scraper that runs at configurable intervals and scrapes only new posts.

## Quick Start

```bash
pip install requests beautifulsoup4
# Continuous mode (default)
python scraper.py
# Single-run mode
python scraper.py --once
```

Setup prompts:
```
Enter subreddit name (without r/): Python
Scraping interval in minutes (default: 60): 30
Output directory (default: data): data
```

## Features

- **Automated scraping** at configurable intervals (default: 60 min)
- **Smart deduplication** - only scrapes new posts
- **Database tracking** - SQLite database
- **Multiple formats** - JSON and CSV output
- **Free API** - uses Reddit's JSON API (no auth required)

## How It Works

1. **Initial run**: Scrapes latest 100 posts, saves to database
2. **Subsequent runs**: Fetches latest posts, saves only new ones
3. **Data storage**: SQLite database + JSON/CSV files

## Configuration

- **Subreddit**: Any public subreddit (e.g., `Python`, `technology`)
- **Interval**: Configurable in minutes (min: 5 min)
- **Output**: `data/scraped/{csv,json}/`
- **Database**: `data/db/reddit_scraper.db`

## Data Fields

| Field | Description |
|-------|-------------|
| `post_id` | Unique Reddit post ID |
| `title` | Post title |
| `author` | Username |
| `score` | Upvotes - downvotes |
| `num_comments` | Comment count |
| `created_utc` | Creation timestamp |
| `subreddit` | Subreddit name |
| `scraped_at` | When scraped |

## Usage Examples

```bash
# Continuous mode (default)
python scraper.py --subreddit Python --interval 30

# Single-run mode (run once and exit)
python scraper.py --once --subreddit Python

# Multiple subreddits (run in separate terminals)
python scraper.py --subreddit Python
python scraper.py --subreddit technology

# Programmatic usage
from scraper import RedditAutoScraper
scraper = RedditAutoScraper(subreddit='programming')
scraper.start_auto_scraper(interval_minutes=30)
```

## Output Files

- **JSON**: `data/scraped/json/reddit_auto_[subreddit]_[timestamp].json`
- **CSV**: `data/scraped/csv/reddit_auto_[subreddit]_[timestamp].csv`
- **Database**: `data/db/reddit_scraper.db`
- **Logs**: `data/logs/reddit_scraper.log`

## Monitoring

```sql
-- Check total posts
SELECT COUNT(*) FROM scraped_posts WHERE subreddit = 'Python';

-- Recent sessions
SELECT * FROM scraping_sessions ORDER BY session_start DESC LIMIT 5;
``` 