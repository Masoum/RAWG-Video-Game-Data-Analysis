"""
Fetch game data from the RAWG API and load it into a normalized SQLite database.

Usage:
    python fetch_data.py --pages 2500          # ~100,000 games (40 per page)
    python fetch_data.py --pages 50 --verbose  # quick smoke test
"""

import argparse
import os
import sys
import time

import requests
from dotenv import load_dotenv

from utils.db import get_connection, init_db, upsert_lookup, upsert_game, link_game_genre, link_game_platform

RAWG_BASE_URL = "https://api.rawg.io/api/games"
PAGE_SIZE = 40  # RAWG's max page size
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 2


def fetch_page(api_key: str, page: int) -> dict:
    """Fetch a single page of games from RAWG, with basic retry on failure."""
    params = {
        "key": api_key,
        "page": page,
        "page_size": PAGE_SIZE,
        "ordering": "-added",  # most-popular-first tends to give richer/cleaner records
    }
    for attempt in range(1, MAX_RETRIES + 1):
        response = requests.get(RAWG_BASE_URL, params=params, timeout=15)
        if response.status_code == 200:
            return response.json()
        if response.status_code == 429:
            wait = RETRY_BACKOFF_SECONDS * attempt
            print(f"  Rate limited, waiting {wait}s...")
            time.sleep(wait)
            continue
        response.raise_for_status()
    raise RuntimeError(f"Failed to fetch page {page} after {MAX_RETRIES} attempts")


def store_page(conn, results: list[dict]) -> int:
    """Write one page of RAWG results into the database. Returns rows written."""
    count = 0
    for game in results:
        upsert_game(
            conn,
            {
                "id": game["id"],
                "name": game.get("name"),
                "released": game.get("released"),
                "rating": game.get("rating"),
                "ratings_count": game.get("ratings_count"),
                "metacritic": game.get("metacritic"),
                "playtime": game.get("playtime"),
                "added": game.get("added"),
            },
        )
        for genre in game.get("genres") or []:
            upsert_lookup(conn, "genres", genre["id"], genre["name"])
            link_game_genre(conn, game["id"], genre["id"])
        for plat in game.get("platforms") or []:
            p = plat.get("platform") or {}
            if p.get("id") is not None:
                upsert_lookup(conn, "platforms", p["id"], p["name"])
                link_game_platform(conn, game["id"], p["id"])
        count += 1
    conn.commit()
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch RAWG game data into SQLite.")
    parser.add_argument("--pages", type=int, default=100, help="Number of pages to fetch (40 games/page)")
    parser.add_argument("--verbose", action="store_true", help="Print progress every page")
    args = parser.parse_args()

    load_dotenv()
    api_key = os.getenv("RAWG_API_KEY")
    if not api_key:
        sys.exit(
            "Missing RAWG_API_KEY. Copy .env.example to .env and add your key "
            "from https://rawg.io/apidocs"
        )

    init_db()
    conn = get_connection()

    total = 0
    print(f"Fetching {args.pages} pages (~{args.pages * PAGE_SIZE:,} games)...")
    for page in range(1, args.pages + 1):
        data = fetch_page(api_key, page)
        results = data.get("results", [])
        if not results:
            print(f"No more results at page {page}, stopping early.")
            break
        written = store_page(conn, results)
        total += written
        if args.verbose or page % 25 == 0:
            print(f"  page {page}/{args.pages} — {total:,} games stored so far")
        if not data.get("next"):
            print("Reached the last available page.")
            break

    conn.close()
    print(f"Done. {total:,} games stored in data/games.db")


if __name__ == "__main__":
    main()
