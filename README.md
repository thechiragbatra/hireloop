# Hireloop - AI Job Copilot

An AI-powered job copilot that helps job seekers find matching jobs, tailor resumes honestly with faithfulness checks, and track applications.

## Architecture

| Layer | Tech | Deployment |
|-------|------|------------|
| Backend | FastAPI + SQLAlchemy (async) + Alembic | Render (free tier) |
| Database | Supabase Postgres | Supabase |
| Auth | Supabase Auth (email + Google OAuth) | Supabase |
| Storage | Supabase Storage (resumes/cover letters) | Supabase |
| Frontend | React + Vite + TypeScript + Tailwind | GitHub Pages |
| API client | Axios with Supabase JWT interceptors | GitHub Pages |

## Repo layout

```
hireloop-1/
├── backend/              # FastAPI app (app/), migrations, tests
├── frontend/             # React SPA (src/, vite.config.ts)
├── .github/workflows/    # CI/CD: frontend deploy to GitHub Pages
├── Makefile              # backend dev targets
├── PRIVACY.md            # privacy policy
└── README.md             # this file
```

## Prerequisites

- Python 3.12
- Node.js 20+

## Backend setup

```bash
# Create virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# Install dependencies
cd backend
pip install -e ".[dev]"

# Environment
cp .env.example .env   # fill in real values; never commit .env

# Run
make run          # uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# or
uvicorn app.main:app --reload
```

Backend dev targets (`make`):
- `install` — pip install
- `run` — start uvicorn
- `test` — pytest
- `lint` — ruff check
- `format` — ruff format
- `typecheck` — mypy

## Frontend setup

```bash
cd frontend
npm install

# Environment
cp .env.example .env.local   # fill in VITE_API_URL, VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY

# Dev server
npm run dev                  # http://localhost:5173

# Production build (GitHub Pages base path /hireloop-1/)
VITE_BASE=/hireloop-1/ npm run build   # output: frontend/dist/

# Preview production build locally
npm run preview
```

## GitHub Pages deployment

The frontend deploys automatically via GitHub Actions on push to `main` (`.github/workflows/frontend.yml`).

1. Enable GitHub Pages in repo **Settings → Pages** (source: GitHub Actions).
2. Add repo **Settings → Secrets and variables → Actions**:
   - `VITE_API_URL` — your Render backend URL (e.g. `https://hireloop-api.onrender.com`)
   - `VITE_SUPABASE_URL` — your Supabase project URL
   - `VITE_SUPABASE_ANON_KEY` — your Supabase anon (public) key
3. Push to `main` → workflow builds `frontend/dist` and deploys to `https://thechiragbatra.github.io/hireloop-1/`.

## Features

- Resume parsing (PDF/DOCX) → structured profile
- Job discovery from public ATS sources (RemoteOK, Greenhouse, Lever, Ashby, Adzuna)
- Match scoring against your profile
- Honest resume tailoring — only facts from your profile, with source citations
- Faithfulness verification — detects fabricated claims
- Apply kit generation (tailored resume + cover letter, manual submission only)
- Application tracker
- Supabase Auth: email/password, Google OAuth, protected routes
- Row-Level Security (RLS) on every user table, scoped to `auth.uid()`
- Rate limiting per IP + path
- Async SQLAlchemy + Alembic migrations

## Privacy

See [PRIVACY.md](PRIVACY.md). Key points:

- All user data scoped to the authenticated user via RLS policies.
- Uploaded resumes and cover letters stored in a private Supabase Storage bucket, accessed via signed URLs only.
- No scraping of LinkedIn, Naukri, or Indeed — only public ATS APIs.
- Data never logged; only IDs, sizes, and timings.

## Cost & constraints

- Render free tier: 512 MB RAM, cold starts — keep-warm cron recommended.
- No `torch`/cross-encoder in the production image; hosted embeddings/reranker behind `Embedder`/`Reranker` interfaces; cross-encoder allowed only in offline `evals/`.
- Hireloop does not auto-submit applications — apply kits are for manual submission only.
