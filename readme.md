This is a FastAPI (Python) project with PostgreSQL + Redis + Celery. Two ways to run it:
Option 1: Docker (easiest)
docker compose up --build
Starts API at http://localhost:8000 (Postgres + Redis included). Then run migrations/seed in a second terminal:
docker compose exec api alembic upgrade head
docker compose exec api python -m scripts.seed
Option 2: Local (uses the venv/ already in the repo)
1. Start Postgres & Redis (via Docker only):
docker compose up -d db redis
2. Copy env config (.env already exists — verify it matches your DB):
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
3. Run migrations & seed:
alembic upgrade head
python -m scripts.seed
4. Start the server:
uvicorn app.main:app --reload
Optional worker: celery -A app.worker.celery_app worker --loglevel=info
Docs / testing
- Interactive API docs: http://localhost:8000/docs
- OTP is mocked in dev — check the server logs for the OTP code
- Admin login: admin@mahalaxmipuja.com / admin123 (after seeding)
One caution: your .env may contain real production secrets (Razorpay/Twilio keys). Before pushing this repo anywhere, verify docker-compose.yml default DB creds are fine and no secrets leak.