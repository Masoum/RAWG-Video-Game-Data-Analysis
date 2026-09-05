-- Normalized schema for RAWG game data.
-- Games <-> Genres and Games <-> Platforms are many-to-many, so they're
-- modeled through junction tables rather than comma-separated columns.

CREATE TABLE IF NOT EXISTS games (
    id              INTEGER PRIMARY KEY,   -- RAWG game id
    name            TEXT NOT NULL,
    released        DATE,
    rating          REAL,                  -- RAWG user rating, 0-5
    ratings_count   INTEGER,
    metacritic      INTEGER,               -- 0-100, NULL if unrated
    playtime        INTEGER,               -- average playtime in hours
    added           INTEGER,               -- how many users added this game (popularity proxy)
    fetched_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS genres (
    id      INTEGER PRIMARY KEY,
    name    TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS platforms (
    id      INTEGER PRIMARY KEY,
    name    TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS game_genres (
    game_id     INTEGER NOT NULL REFERENCES games(id) ON DELETE CASCADE,
    genre_id    INTEGER NOT NULL REFERENCES genres(id) ON DELETE CASCADE,
    PRIMARY KEY (game_id, genre_id)
);

CREATE TABLE IF NOT EXISTS game_platforms (
    game_id     INTEGER NOT NULL REFERENCES games(id) ON DELETE CASCADE,
    platform_id INTEGER NOT NULL REFERENCES platforms(id) ON DELETE CASCADE,
    PRIMARY KEY (game_id, platform_id)
);

CREATE INDEX IF NOT EXISTS idx_games_released ON games(released);
CREATE INDEX IF NOT EXISTS idx_games_rating ON games(rating);
CREATE INDEX IF NOT EXISTS idx_game_genres_genre ON game_genres(genre_id);
CREATE INDEX IF NOT EXISTS idx_game_platforms_platform ON game_platforms(platform_id);
