# Reddit Data Mining & Word Analysis (Modern Version)

A full-stack system for automated Reddit scraping, live word frequency analysis, and interactive exploration via a modern React UI.

---

## Quick Start

### 1. Backend (FastAPI)
```bash
cd backend/app
pip install -r requirements.txt
uvicorn main:app --reload
```

### 2. Frontend (React + Vite)
```bash
cd ui
npm install
npm run dev
```

---

## Features
- **Live Reddit Scraping:** Scrape any subreddit on demand, specifying the number of posts.
- **Incremental Word Frequency Analysis:** Word frequencies are updated after every scrape and can be re-analyzed at any time.
- **Subreddit-Filtered Top Words:** Instantly filter top words by subreddit in the UI.
- **Modern UI:** Beautiful, responsive React frontend with Material-UI components.
- **Database-Only Storage:** All data is stored in PostgreSQL/SQLite; no CSV/JSON file outputs.
- **API-Driven:** All features are accessible via documented REST API endpoints.

---

## Database Schema (Key Tables)
- `scraped_posts`: All scraped Reddit posts.
- `word_frequencies`: Word counts per (word, subreddit).
- `scraped_subreddits`: List of all subreddits ever scraped (drives the UI filter dropdown).
- `scraping_sessions`: Metadata for each scraping session.

---

## API Endpoints (Highlights)
- `POST /scraper/run-once` — Scrape a subreddit (specify subreddit and number of posts).
- `GET /analyzer` — Get top words, optionally filtered by subreddit.
- `GET /analyzer/subreddits` — List all subreddits ever scraped.
- `POST /analyzer/incremental` — Run incremental word frequency analysis.
- `GET /db/stats` — Get database statistics.

---

## UI Features
- **Subreddit Filter:** Dropdown shows all scraped subreddits (live from DB).
- **Top Words Table:** Shows most frequent words for the selected subreddit.
- **Scrape Controls:** Choose subreddit and number of posts, trigger scrape, and run incremental analysis from the UI.
- **Live Updates:** All data is fetched live from the backend after each operation.

---

## How to Use
1. Start the backend and frontend as above.
2. In the UI, select a subreddit and number of posts, then click "Run Scraper & Analyze".
3. Use the filter dropdown to explore top words by subreddit.
4. Click "Incremental Analyze" to re-analyze word frequencies at any time.

---

## Configuration
- **Database:** Uses PostgreSQL or SQLite (see `backend/app/core/utils/config.py`).
- **Logging:** Logs are stored in `data/logs/`.
- **No file outputs:** All analysis is stored in the database and accessed via API/UI.

---

## Project Structure (Key Parts)
```
backend/app/
  api/           # FastAPI endpoints
  core/          # Scraper, analyzer, database logic
  main.py        # FastAPI app entry point
ui/              # React frontend (Vite + MUI)
```

---

## Authors & License
MIT License. Modernized and maintained by your team. 