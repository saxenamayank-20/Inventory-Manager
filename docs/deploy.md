# Deploy notes

The backend runs on Render, the frontend on Streamlit Cloud and the database on Clever Cloud (MySQL). Pushing to `main` redeploys both apps.

## Database (Clever Cloud)

Open the MySQL add-on → Environment variables and note `MYSQL_ADDON_HOST`, `MYSQL_ADDON_PORT`, `MYSQL_ADDON_DB`, `MYSQL_ADDON_USER` and `MYSQL_ADDON_PASSWORD`.

The backend wants them as one URL:

```
mysql+pymysql://USER:PASSWORD@HOST:PORT/DB
```

If the password has `@ # / : ?` or `%` in it, encode those characters (`@` → `%40`, `#` → `%23`).

## Backend (Render)

| Setting | Value |
|---|---|
| Branch | `main` |
| Root Directory | empty |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn backend.main:app --host 0.0.0.0 --port $PORT` |
| Health Check Path | `/` |

Environment variables:

| Key | Value |
|---|---|
| `DATABASE_URL` | the MySQL URL above |
| `PYTHON_VERSION` | `3.12.3` |

Tables get created on the first start. The free plan sleeps after a while, so the first request after that is slow.

## Frontend (Streamlit Cloud)

- Main file: `frontend/app.py`
- It talks to the Render backend by default. To point it somewhere else, add `BACKEND_URL` in the app's secrets.
- The dark theme comes from `.streamlit/config.toml`.

## Common errors

| Error in Render logs | Fix |
|---|---|
| `Access denied` / `Unknown database` | wrong user, password or db name in `DATABASE_URL`, or a special character in the password isn't encoded |
| `Can't connect to MySQL server` | wrong host or port |
| `Too many connections` | Clever Cloud's free MySQL allows very few connections, so the SQLAlchemy pool needs to be smaller |
| `cryptography package is required` | PyMySQL needs the `cryptography` package for this MySQL login method |
