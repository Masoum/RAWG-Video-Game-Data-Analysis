"""
RAWG Game Data Explorer — an interactive Streamlit dashboard for exploring
video game trends by genre, platform, rating, and release year.

Run with: streamlit run app.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from utils.db import get_connection, DB_PATH

st.set_page_config(page_title="RAWG Game Data Explorer", layout="wide")


@st.cache_data(ttl=3600)
def load_lookup(table: str) -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql(f"SELECT id, name FROM {table} ORDER BY name", conn)


@st.cache_data(ttl=3600)
def load_games(genre_ids: tuple, platform_ids: tuple, year_range: tuple, min_rating: float) -> pd.DataFrame:
    """Query games joined against the selected genre/platform filters."""
    query = """
        SELECT DISTINCT g.id, g.name, g.released, g.rating, g.ratings_count,
               g.metacritic, g.playtime, g.added
        FROM games g
    """
    joins = []
    where = ["g.released IS NOT NULL", "g.rating >= :min_rating"]
    params = {"min_rating": min_rating}

    if genre_ids:
        joins.append("JOIN game_genres gg ON gg.game_id = g.id")
        placeholders = ",".join(f":genre{i}" for i in range(len(genre_ids)))
        where.append(f"gg.genre_id IN ({placeholders})")
        params.update({f"genre{i}": gid for i, gid in enumerate(genre_ids)})

    if platform_ids:
        joins.append("JOIN game_platforms gp ON gp.game_id = g.id")
        placeholders = ",".join(f":plat{i}" for i in range(len(platform_ids)))
        where.append(f"gp.platform_id IN ({placeholders})")
        params.update({f"plat{i}": pid for i, pid in enumerate(platform_ids)})

    if year_range:
        where.append("CAST(strftime('%Y', g.released) AS INTEGER) BETWEEN :year_start AND :year_end")
        params["year_start"], params["year_end"] = year_range

    query += " " + " ".join(joins)
    query += " WHERE " + " AND ".join(where)

    with get_connection() as conn:
        df = pd.read_sql(query, conn, params=params, parse_dates=["released"])
    return df


def empty_state():
    st.warning(
        "No data found. Run `python fetch_data.py --pages 100` first to populate "
        "`data/games.db` (see README.md for setup)."
    )
    st.stop()


def main():
    st.title("🎮 RAWG Game Data Explorer")
    st.caption(
        "Exploring trends across 100,000+ games — filter by genre, platform, "
        "rating, and release year to see what's driving the numbers."
    )

    if not Path(DB_PATH).exists():
        empty_state()

    genres_df = load_lookup("genres")
    platforms_df = load_lookup("platforms")

    if genres_df.empty or platforms_df.empty:
        empty_state()

    # --- Sidebar filters ---
    st.sidebar.header("Filters")
    genre_names = st.sidebar.multiselect("Genre", genres_df["name"].tolist())
    platform_names = st.sidebar.multiselect("Platform", platforms_df["name"].tolist())
    year_range = st.sidebar.slider("Release year", 1980, 2026, (2000, 2026))
    min_rating = st.sidebar.slider("Minimum rating", 0.0, 5.0, 0.0, step=0.1)

    genre_ids = tuple(genres_df.loc[genres_df["name"].isin(genre_names), "id"])
    platform_ids = tuple(platforms_df.loc[platforms_df["name"].isin(platform_names), "id"])

    df = load_games(genre_ids, platform_ids, year_range, min_rating)

    if df.empty:
        st.info("No games match the current filters — try widening your selection.")
        st.stop()

    # --- Headline metrics ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Games matched", f"{len(df):,}")
    col2.metric("Avg. rating", f"{df['rating'].mean():.2f} / 5")
    col3.metric("Avg. playtime", f"{df['playtime'].mean():.1f} hrs")
    col4.metric("Avg. metacritic", f"{df['metacritic'].dropna().mean():.0f}" if df["metacritic"].notna().any() else "n/a")

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Games released per year")
        by_year = df.assign(year=df["released"].dt.year).groupby("year").size()
        st.bar_chart(by_year)

    with right:
        st.subheader("Rating distribution")
        fig, ax = plt.subplots()
        ax.hist(df["rating"].dropna(), bins=20, color="#4C78A8", edgecolor="white")
        ax.set_xlabel("Rating")
        ax.set_ylabel("Number of games")
        st.pyplot(fig)

    st.subheader("Top games by popularity ('added' count)")
    top_games = df.sort_values("added", ascending=False).head(20)[
        ["name", "released", "rating", "metacritic", "added"]
    ]
    st.dataframe(top_games, use_container_width=True, hide_index=True)

    with st.expander("Show raw filtered data"):
        st.dataframe(df, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
