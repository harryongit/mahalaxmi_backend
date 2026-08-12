# MahalaxmiPuja Backend

FastAPI backend for MahalaxmiPuja.com (PostgreSQL + optional Redis + Celery).

## Requirements

- Python 3.11+ (a `venv/` is already bundled)
- PostgreSQL running locally (port 5432) with database `mahalaxmi`
- Redis is **optional** — if not running, the app falls back to an in-memory store (dev mode)

## Setup

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Make sure `.env` exists (copy from `.env.example`) and `DATABASE_URL` matches your local PostgreSQL.

## Run the app

```powershell
alembic upgrade head
python -m scripts.seed
uvicorn app.main:app --reload
```

- API docs: http://localhost:8000/docs
- OTP is mocked in dev — the code is printed in the server logs
- Admin login: `admin@mahalaxmipuja.com` / `admin123` (after seeding)

## Optional: Celery worker (background notifications)

Only needed for real WhatsApp/email delivery:

```powershell
celery -A app.worker.celery_app worker --loglevel=info
```

Without a worker, notifications are skipped with a warning instead of crashing.

## Tests

```powershell
python -m pytest tests -v
```

Tests use SQLite + an in-memory Redis fake — no Docker, Postgres or Redis required.

## Note

`.env` may contain real Razorpay keys. Do not commit `.env` to the repo (it is gitignored).