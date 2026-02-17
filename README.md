<div align="center">
<table><tr>
<td><h1>BGG Pipeline</h1><p>A data pipeline that scrapes board game rankings, statistics, and mechanics from <a href="https://boardgamegeek.com">BoardGameGeek</a> and stores them in a local SQLite database.</p></td>
<td><img src="https://cf.geekdo-images.com/HZy35cmzmmyV9BarSuk6ug__imagepage/img/FOGhR5OgYhcg-1jdqT5i5W8Xfbg=/fit-in/900x600/filters:no_upscale():strip_icc()/pic7779581.png" alt="BoardGameGeek Logo" width="200"></td>
</tr></table>
</div>

## Overview

The pipeline runs in three phases:

1. **Game Rankings** - Scrapes the BGG browse/rankings HTML pages to collect game IDs, names, and ranks.
2. **Game Statistics** - Queries the BGG XML API for each game to collect statistics (player counts, ratings, weight, etc.) and saves the raw XML responses to disk.
3. **Game Mechanics** - Parses the saved XML files to extract game mechanics (e.g. deck building, dice rolling).

All collected data is validated with Pydantic schemas and bulk-inserted into a SQLite database at `data/bgg_data.db`.

## Project Structure

```
bgg_pipeline/
├── src/
│   ├── pipeline.py          # Main pipeline orchestration
│   ├── database.py          # SQLAlchemy engine, session management, bulk insert
│   ├── models.py            # SQLAlchemy table models (Games, Statistics, Mechanics)
│   ├── schemas.py           # Pydantic validation schemas
│   ├── sources/
│   │   ├── html_pages.py    # Fetches BGG ranking HTML pages
│   │   └── xml_api.py       # Fetches game data from BGG XML API
│   ├── parsers/
│   │   ├── html_parsers.py  # Parses ranking data from HTML
│   │   └── xml_parsers.py   # Parses statistics and mechanics from XML
│   └── utils/
│       ├── api_auth.py      # API authentication handling
│       ├── make_requests.py # HTTP request utilities
│       ├── throttler.py     # Rate limiting for API requests
│       └── logging_config.py
├── tests/                   # Pytest test suite
├── data/
│   ├── bgg_data.db          # SQLite database (output)
│   ├── raw_html/            # Cached HTML pages
│   └── raw_xmls/            # Cached XML API responses
└── pyproject.toml
```

## Database Schema

| Table        | Columns                                                                                              |
|--------------|------------------------------------------------------------------------------------------------------|
| **Games**    | `id` (PK), `rank`, `name`                                                                           |
| **Statistics** | `id` (FK -> Games), `description`, `year_published`, `min_players`, `max_players`, `suggested_num_player`, `min_age`, `average_rating`, `average_weight` |
| **Mechanics** | `id` (FK -> Games), `mechanic` (composite PK)                                                       |

## Requirements

- Python 3.13

## Setup

1. Install dependencies with [Poetry](https://python-poetry.org/):

   ```bash
   poetry install
   ```

2. Add your BGG credentials to `bgg_auth.txt` (used for API authentication).

## Usage

Run the full pipeline:

```bash
poetry run python src/pipeline.py
```

The pipeline will:
- Scrape game rankings from BGG
- Fetch statistics for each game via the XML API
- Extract mechanics from the saved XML files
- Store everything in `data/bgg_data.db`

## Testing

```bash
poetry run pytest
```
