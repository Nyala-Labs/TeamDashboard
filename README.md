# TeamDashboard

Nyala Labs platform for committee members to manage team communications.

**Stack:** Next.js (Vercel) + FastAPI (Serverless) + Supabase (PostgreSQL).

## Local development (no Docker)

### 1. Database
Use [Supabase](https://supabase.com) (free tier) or a local PostgreSQL instance.

### 2. Backend
```bash
cd backend
uv sync
cp .env.example .env
# Edit .env: set DATABASE_URL (Supabase pooler URL or local postgres)
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8000
```

### 3. Frontend
```bash
cd frontend
npm install
cp ../.env.example .env.local
# Edit .env.local: set NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

### 4. Migrations
```bash
cd backend
uv run alembic revision --autogenerate -m "description"
uv run alembic upgrade head
```

## Vercel deployment
- Connect the repo to Vercel; set **Root Directory** to `frontend`.
- Add env vars: `DATABASE_URL` (from Supabase), optionally `NEXT_PUBLIC_API_URL` (leave empty for same-origin).
