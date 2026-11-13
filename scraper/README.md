# Thread scraper

Digest of internship / skills threads (Hacker News, Reddit) plus new, fast-growing GitHub repos.
No dependencies, Python 3.

    python scraper/scrape.py                    # all sources
    python scraper/scrape.py --only github -o digest.md
    python scraper/scrape.py --days 14 --top 20

Edit `HN_QUERIES`, `SUBREDDITS`, `GH_TOPICS` at the top of `scrape.py` to change what it tracks.
Optional: `export GITHUB_TOKEN=...` for higher GitHub rate limits.
