#!/usr/bin/env python3
"""Thread scraper: internships, skills, and hyped/new GitHub repos.

Sources (no API keys needed, stdlib only):
  - Hacker News (Algolia API)
  - Reddit (public .json endpoints)
  - GitHub (search API: new repos that are gaining stars fast)

Usage:
  python scraper/scrape.py                 # print markdown digest
  python scraper/scrape.py -o digest.md    # write to file
  python scraper/scrape.py --days 14 --limit 15 --only github
Set GITHUB_TOKEN to raise GitHub rate limits (optional).
"""
import argparse, json, os, sys, time, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone

UA = "thread-scraper/0.1 (personal learning project)"

HN_QUERIES = ["internship", "summer internship", "learn to code roadmap",
              "skills in demand", "new grad hiring"]
SUBREDDITS = ["internships", "cscareerquestions", "learnprogramming",
              "csMajors", "opensource"]
GH_TOPICS = ["", "ai", "llm", "agents", "rust", "devtools"]


def get(url, headers=None):
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.load(r)
        except Exception as e:
            if attempt == 2:
                print(f"[warn] {url[:80]}... failed: {e}", file=sys.stderr)
                return None
            time.sleep(1.5 * (attempt + 1))


def hacker_news(days, limit):
    since = int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp())
    out = {}
    for q in HN_QUERIES:
        params = urllib.parse.urlencode({
            "query": q, "tags": "story", "hitsPerPage": limit,
            "numericFilters": f"created_at_i>{since},points>10"})
        data = get(f"https://hn.algolia.com/api/v1/search?{params}")
        for h in (data or {}).get("hits", []):
            out[h["objectID"]] = {
                "source": "HN", "title": h.get("title"),
                "url": f"https://news.ycombinator.com/item?id={h['objectID']}",
                "score": h.get("points", 0) + 2 * h.get("num_comments", 0),
                "meta": f"{h.get('points', 0)} pts, {h.get('num_comments', 0)} comments"}
    return list(out.values())


def reddit(days, limit):
    window = "week" if days <= 7 else "month"
    out = []
    for sub in SUBREDDITS:
        data = get(f"https://www.reddit.com/r/{sub}/top.json?t={window}&limit={limit}")
        for c in (data or {}).get("data", {}).get("children", []):
            d = c["data"]
            out.append({
                "source": f"r/{sub}", "title": d["title"],
                "url": "https://reddit.com" + d["permalink"],
                "score": d["score"] + 2 * d["num_comments"],
                "meta": f"{d['score']} upvotes, {d['num_comments']} comments"})
        time.sleep(1)  # be polite
    return out


def github(days, limit):
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    headers = {"Accept": "application/vnd.github+json"}
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    out = {}
    for topic in GH_TOPICS:
        q = f"created:>{since} stars:>50" + (f" topic:{topic}" if topic else "")
        params = urllib.parse.urlencode({"q": q, "sort": "stars", "order": "desc",
                                         "per_page": limit})
        data = get(f"https://api.github.com/search/repositories?{params}", headers)
        for r in (data or {}).get("items", []):
            age = max(1, (datetime.now(timezone.utc) - datetime.fromisoformat(
                r["created_at"].replace("Z", "+00:00"))).days)
            out[r["full_name"]] = {
                "source": "GitHub", "title": f"{r['full_name']} - {r['description'] or ''}"[:140],
                "url": r["html_url"],
                "score": r["stargazers_count"] / age * 7,  # stars/week = "hype"
                "meta": f"{r['stargazers_count']} stars, {age}d old, "
                        f"~{r['stargazers_count'] // age}/day, {r['language'] or 'n/a'}"}
        time.sleep(2)  # search API: 10 req/min unauthenticated
    return list(out.values())


SOURCES = {"hn": hacker_news, "reddit": reddit, "github": github}


def render(items, top):
    lines = [f"# Internships, skills & hyped repos - {datetime.now():%Y-%m-%d}\n"]
    for src in ("GitHub", "HN", "r/"):
        group = sorted((i for i in items if i["source"].startswith(src)),
                       key=lambda i: -i["score"])[:top]
        if not group:
            continue
        lines.append(f"\n## {'GitHub - new & trending repos' if src == 'GitHub' else 'Hacker News' if src == 'HN' else 'Reddit'}\n")
        for i in group:
            tag = f"[{i['source']}] " if src == "r/" else ""
            lines.append(f"- {tag}[{i['title']}]({i['url']}) - {i['meta']}")
    return "\n".join(lines) + "\n"


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--days", type=int, default=7, help="look-back window (default 7)")
    p.add_argument("--limit", type=int, default=10, help="results per query")
    p.add_argument("--top", type=int, default=15, help="items shown per section")
    p.add_argument("--only", choices=SOURCES, help="run a single source")
    p.add_argument("-o", "--output", help="write markdown to this file")
    a = p.parse_args()
    items = []
    for name, fn in SOURCES.items():
        if a.only in (None, name):
            items += fn(a.days, a.limit)
    md = render(items, a.top)
    if a.output:
        with open(a.output, "w") as f:
            f.write(md)
        print(f"wrote {len(items)} items to {a.output}")
    else:
        print(md)


if __name__ == "__main__":
    main()
