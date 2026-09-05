# # RAWG Game Data Explorer

An interactive Streamlit dashboard for exploring 100,000+ video game records pulled
from the [RAWG Video Games Database API](https://rawg.io/apidocs). Built to practice
API ingestion, SQL data modeling, and self-serve dashboard design for non-technical users.

## What it does

- **Ingests** game data (name, release date, rating, metacritic score, genres,
  platforms, playtime, popularity) from the RAWG API into a normalized SQLite database.
- **Explores trends** by genre, platform, rating, and release year through an
  interactive Streamlit app — no code required to filter or drill down.
- **Visualizes** rating distributions, genre popularity over time, and
  platform market share using Matplotlib and native Streamlit charts.

## Architecture

```
rawg-dashboard/
├── fetch_data.py        # Pulls data from the RAWG API, paginates, writes to SQLite
├── schema.sql            # Normalized table definitions (games, genres, platforms, junctions)
├── app.py                 # Streamlit dashboard — reads from SQLite via pandas.read_sql
├── utils/
│   └── db.py             # Shared DB connection + query helpers
├── data/
│   └── games.db           # SQLite database (created by fetch_data.py, gitignored)
├── requirements.txt
├── .env.example
└── .streamlit/
    └── config.toml        # Basic theming for the app
```

### Why a normalized schema?

Genres and platforms are many-to-many with games (a game can have several of each),
so they're modeled as separate `genres` / `platforms` tables joined through
`game_genres` / `game_platforms` junction tables rather than stuffed into
comma-separated strings. This makes filtering and aggregation ("average rating
per genre", "top platforms by release year") a straightforward SQL `JOIN` +
`GROUP BY` instead of string parsing.

## Setup

1. **Get a free RAWG API key**: sign up at https://rawg.io/apidocs and copy your key.

2. **Clone and install dependencies**

   ```bash
   git clone <your-repo-url>
   cd rawg-dashboard
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure your API key**

   ```bash
   cp .env.example .env
   # then edit .env and paste your RAWG_API_KEY
   ```

4. **Fetch the data** (this builds `data/games.db`; adjust `--pages` for a
   smaller/larger pull — each page is ~40 games)

   ```bash
   python fetch_data.py --pages 2500
   ```

5. **Run the dashboard**

   ```bash
   streamlit run app.py
   ```

   Then open the local URL Streamlit prints (usually http://localhost:8501).

## Roadmap / ideas to extend

- [ ] Add a "compare two genres" side-by-side view
- [ ] Cache RAWG API responses to avoid re-fetching on reruns
- [ ] Deploy to Streamlit Community Cloud and link a live demo here
- [ ] Add a scheduled refresh (GitHub Actions cron) to keep the dataset current
- [ ] Swap SQLite for PostgreSQL and add a docker-compose for local dev

## Screenshots

_Add a screenshot or GIF of the running dashboard here once deployed —
this is what recruiters/hiring managers will actually look at first._

## Tech stack

Python · Streamlit · pandas · SQLite · Matplotlib · RequestsRAWG-Video-Game-Data-Analysis
