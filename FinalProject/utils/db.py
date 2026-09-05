"""Shared SQLite connection and query helpers for the RAWG dashboard."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "games.db"
SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schema.sql"


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection with foreign keys enabled."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db() -> None:
    """Create tables/indexes from schema.sql if they don't already exist."""
    with get_connection() as conn:
        conn.executescript(SCHEMA_PATH.read_text())


def upsert_lookup(conn: sqlite3.Connection, table: str, id_: int, name: str) -> None:
    """Insert a genre/platform row if it doesn't already exist."""
    conn.execute(
        f"INSERT OR IGNORE INTO {table} (id, name) VALUES (?, ?)", (id_, name)
    )


def upsert_game(conn: sqlite3.Connection, game: dict) -> None:
    """Insert or update a single game row."""
    conn.execute(
        """
        INSERT INTO games (id, name, released, rating, ratings_count, metacritic, playtime, added)
        VALUES (:id, :name, :released, :rating, :ratings_count, :metacritic, :playtime, :added)
        ON CONFLICT(id) DO UPDATE SET
            name=excluded.name,
            released=excluded.released,
            rating=excluded.rating,
            ratings_count=excluded.ratings_count,
            metacritic=excluded.metacritic,
            playtime=excluded.playtime,
            added=excluded.added
        """,
        game,
    )


def link_game_genre(conn: sqlite3.Connection, game_id: int, genre_id: int) -> None:
    conn.execute(
        "INSERT OR IGNORE INTO game_genres (game_id, genre_id) VALUES (?, ?)",
        (game_id, genre_id),
    )


def link_game_platform(conn: sqlite3.Connection, game_id: int, platform_id: int) -> None:
    conn.execute(
        "INSERT OR IGNORE INTO game_platforms (game_id, platform_id) VALUES (?, ?)",
        (game_id, platform_id),
    )
