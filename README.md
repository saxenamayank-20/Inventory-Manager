# Inventory Manager

A small app I built to add, edit, search and delete items in a product inventory. It has a FastAPI backend, a MySQL database and a Streamlit frontend.

![Dashboard](docs/screenshots/dashboard.png)

<p>
  <img src="docs/screenshots/add-item.png" width="49%" alt="Add item page">
  <img src="docs/screenshots/search.png" width="49%" alt="Search page">
</p>

## Why I built it

I wanted to build a full CRUD app with a separate frontend and backend, and deploy each part on its own free host. Keeping stock in a spreadsheet gets messy fast, so an inventory app was a good fit.

## Features

- Dashboard with total products, total quantity, inventory value and average price
- Table of all items
- Add an item (name, price, quantity, optional description)
- Load an item by ID and update any of its fields
- Preview an item before deleting it
- Search items by name (partial, case-insensitive)
- API status indicator in the sidebar
- Swagger docs for the API at `/docs`

## Tech stack

- Python 3.12
- FastAPI 0.142 + Uvicorn
- SQLAlchemy 2.1 + PyMySQL
- Pydantic 2
- Streamlit 1.65 + pandas
- MySQL (Clever Cloud) in production, SQLite locally if no `DATABASE_URL` is set
- pytest for the API tests

Hosting: the backend is on Render, the frontend on Streamlit Cloud, and the database on Clever Cloud. Setup notes are in [docs/deploy.md](docs/deploy.md).

## How it works

The Streamlit app never talks to the database directly. It calls the FastAPI backend over HTTP with `requests`, and the backend reads and writes MySQL through SQLAlchemy. Tables are created on startup if they don't exist.

```mermaid
flowchart LR
    U[User] --> F["Streamlit frontend<br/>(Streamlit Cloud)"]
    F -- "HTTP / JSON" --> B["FastAPI backend<br/>(Render)"]
    B -- "SQLAlchemy + PyMySQL" --> D[("MySQL<br/>(Clever Cloud)")]
```

## Run it locally

Prerequisites: Python 3.11+ and git. MySQL is optional: without it the backend uses a local SQLite file.

```bash
git clone https://github.com/saxenamayank-20/Inventory_Manager.git
cd Inventory_Manager

python3 -m venv .venv
source .venv/bin/activate        # windows: .venv\Scripts\activate

pip install -r requirements.txt
```

Create a `.env` file in the project root. Both variables are optional:

- `DATABASE_URL`: MySQL connection string (`mysql://user:password@host:port/db`). Without it the backend uses SQLite.
- `BACKEND_URL`: where the frontend finds the API. Set it to `http://127.0.0.1:8000` to use your local backend. Without it the frontend uses the Render backend.

Start the backend (terminal 1):

```bash
uvicorn backend.main:app --reload
```

The API runs at http://127.0.0.1:8000, with docs at http://127.0.0.1:8000/docs.

Start the frontend (terminal 2, with the `.venv` activated):

```bash
streamlit run frontend/app.py
```

The app opens at http://localhost:8501.

## API routes

| Method | Route | What it does |
|--------|-------|--------------|
| GET | `/` | Health check |
| GET | `/items` | List items (`skip`, `limit` query params, default 100) |
| POST | `/items` | Create an item |
| GET | `/items/search?keyword=` | Search by name, 404 if nothing matches |
| GET | `/items/{item_id}` | Get one item |
| PUT | `/items/{item_id}` | Update only the fields you send |
| DELETE | `/items/{item_id}` | Delete an item |

## Project structure

```
backend/      fastapi app, db setup, models, schemas, crud
frontend/     streamlit app
tests/        api tests (pytest, sqlite)
docs/         screenshots and deploy notes
.streamlit/   streamlit theme config
```

## Running tests

```bash
python -m pytest
```

The tests use a temporary SQLite database, so they never touch the real MySQL one.

## What I learned

- Render's free plan sleeps, so the first request can take close to a minute. The frontend now waits longer and shows an error instead of crashing if the backend doesn't answer.
- `pymysql` has to be in `requirements.txt`. A `mysql+pymysql://` URL fails on startup without it.
- On partial updates, a field sent as `null` is different from a field not sent at all. Name, price and quantity now ignore `null`, and description can still be cleared.
- Custom dark CSS on top of Streamlit's light theme made the text unreadable. Setting the dark theme in `.streamlit/config.toml` fixed it.

## Known limitations and what's next

- Render's free plan sleeps, so the first load is slow.
- There's no login. Anyone with the link can add or delete items.
- The dashboard only shows the first 100 items.
- Update and delete need you to type the item ID.
- CORS allows all origins.
