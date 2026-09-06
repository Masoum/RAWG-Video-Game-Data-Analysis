# RAWG Game Data Explorer

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


## Data Cleaning  
Data cleaning is essential for robust analysis. The initial dataset consisted of 33 columns, many of which contained JSON data stored as strings. Several columns were entirely empty (e.g., `user_game`, `clip`), and others such as `esrb_rating`, `metacritic`, and `community_rating` had many missing values. Stringified JSON columns containing complex data—such as `ratings`, `genres`, and `platforms`—were parsed into usable formats.  
After cleaning, the dataset comprises 24 features, including:  
- `id`, `name`, `released`, `tba`, `rating`, `rating_top`, `ratings`,  
- `ratings_count`, `reviews_text_count`, `added`, `metacritic`,  
- `playtime`, `suggestions_count`, `reviews_count`, `platforms`, `genres`,  
- `esrb_rating`, `genres_list`, `platforms_list`, `year`, `release_year`,  
- `genre_names`, `platform_names`, `esrb_rating_clean`

---

## Analysis

### **Top 10 Platforms (Games After 2014)**  
![Top 10 platforms](TopPlatform.png)

The chart above displays the number of games available on each platform after 2014. PC dominates with the largest library, reflecting its open platform nature, while consoles such as PlayStation 4 and Xbox One follow closely. Notably, newer platforms and consoles tend to feature more games than older systems.

---

### **Game Releases Over the Years**  
![Released Over Years](ReleaseByYear.jpg)

Game releases over time show a clear upward trend. In the early years (1970s–1980s), relatively few titles were released. However, starting in the 1990s—especially after the 2000s—the number of releases accelerated dramatically, illustrating the rapid growth and increasing accessibility of video games. Notably, 2016 stands out as a record year in the industry.

---

### **Average Rating by Genre**  
![Average Rating by Genre](AveRatingByGenere.png)

The average user rating by genre reveals subtle differences: indie and RPG games, for example, score slightly higher on average compared to genres like racing or casual games. However, most genres have average ratings between 3.4 and 3.6, suggesting that overall player satisfaction is fairly consistent across different types of games.

---

### **User Rating vs. Metacritic Score**  
![Rating vs Metacritic](RatingvsMetacritic.png)

This scatter plot demonstrates a strong positive correlation between user ratings and Metacritic scores. Generally, games with high critic scores also receive favorable ratings from players, although a few outliers exist where user sentiment diverges from critic reviews. Overall, the trend indicates that quality is recognized by both audiences and professionals.

---

### **Top Games by Rating**  
![Top 10 Highest Rate](Top10HighestRate.png)

The chart above lists the top 10 games by average user rating (among those with a significant number of ratings). Critically acclaimed titles such as *Red Dead Redemption 2*, *Half-Life 2*, *Portal 2*, and *God of War (2018)* lead the list with average ratings around 4.5–4.7 out of 5. This reflects a highly positive reception from the gaming community, aligning with these titles’ reputation as some of the best in their genres.

---

### **Top Games by Popularity**  
![Most Popular](MostPopular.png)

In contrast, the top 10 most popular games—based on the number of user ratings—highlight titles like *Grand Theft Auto V* and *The Witcher 3: Wild Hunt*. Other popular games, such as *The Elder Scrolls V: Skyrim*, *Portal 2*, and *Counter-Strike*, also exhibit high engagement. Many of these titles overlap with the highest-rated games, suggesting that broad appeal often goes hand-in-hand with high satisfaction.

---

### **User Rating by Percentage**  
![User Rating By Percentage](UsrRatingByPercent.png)

Most users rate games as "recommended" or "exceptional," indicating a generally positive community sentiment.

---

### **Distribution of Average User Ratings**  
![Average User Ratings](AveUsrRating.png)

The distribution of average user ratings is roughly bell-shaped and centered around 3.5 out of 5. Most games receive moderate to good ratings, with the majority falling between 3.0 and 4.5. Extreme ratings (very low or perfect scores) are rare, emphasizing that truly outstanding games are uncommon.




## Tech stack

Python · Streamlit · pandas · SQLite · Matplotlib · Requests
