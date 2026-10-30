# Hireloop

Hireloop helps a job seeker turn a resume into a private profile, discover public job listings, rank them against resume evidence, prepare a fact-grounded resume and cover-letter draft, and track applications. It never submits an application.

## What works

- PDF and DOCX text extraction with contact, skill, experience, project, and education section parsing.
- Job discovery from Remote OK, We Work Remotely, Jobicy, and Himalayas public feeds.
- Resume-to-job ranking. With no model key, a deterministic skill and keyword scorer is used; with an LLM key, the configured model can score matches.
- Tailored resume bullets cite the source profile facts. The no-key fallback copies source bullets verbatim and checks citations locally.
- Apply-kit generation with a cover-letter draft. Review all generated wording before using it.
- Saved applications, status changes, CSV export, and a delete-my-data action.
- Supabase email/password authentication in the browser, verified access tokens in the API, and user-scoped profile/application records.
- SQLAlchemy persistence on SQLite locally and Postgres in production. Alembic owns production schema migrations.

Job feed availability depends on the public providers. Hireloop does not scrape LinkedIn, Indeed, or Naukri. Scanned/image-only PDFs are not OCR processed.

## Run locally

Requirements: Python 3.12 and a modern browser.

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

In local development, the API uses a local SQLite database and a local-only identity when Supabase is not configured. Serve the static frontend in another terminal:

```bash
cd frontend
python3 -m http.server 5173
```

Open `http://localhost:5173`. The tracked `frontend/config.js` points to the local API and leaves Supabase Auth unset. **Do not use local mode for a public deployment or upload real resumes to a public development server.**

An optional LLM key enables model-assisted match scoring, tailoring, verification, and cover letters. Without one, scoring and resume tailoring use the local factual fallback.

## Production deployment

### 1. Create Supabase resources

Create a Supabase project and enable email/password authentication. Configure the allowed redirect URLs to include the GitHub Pages site URL. For Google sign-in, configure Google as an OAuth provider in Supabase and add its callback URL in Google Cloud. Copy the project URL and public anon/publishable key. Do not use a service-role key in the browser. Get the Postgres connection string from Supabase; use its pooler connection if required by your plan/network. Hireloop scopes profile and application rows by the verified JWT subject in the API.

### 2. Deploy the API to Render

Create a Render web service from this repository using the included `render.yaml` blueprint, or configure the service with `backend` as the root directory. Add these environment values in Render:

| Variable | Value |
| --- | --- |
| `APP_ENV` | `production` |
| `DATABASE_URL` | Supabase Postgres connection URI |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_ANON_KEY` | Supabase public anon/publishable key |
| `ALLOWED_CORS_ORIGINS` | JSON list containing `https://thechiragbatra.github.io` and any local origin you need |
| `LLM_API_KEY` | Optional OpenRouter key for model-assisted generation |

The start command runs `alembic upgrade head` before Uvicorn. Confirm Render reports the service healthy at `/health`; note the actual service URL for the next step. Keep the database URI and model key in Render’s environment settings only.

### 3. Configure GitHub Pages

In GitHub repository Settings → Pages, select GitHub Actions. Add these repository **Variables** under Settings → Secrets and variables → Actions → Variables:

| Variable | Value |
| --- | --- |
| `API_BASE_URL` | Render URL ending in `/api/v1` |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_ANON_KEY` | Supabase public anon/publishable key |

Push the desired branch to `main`. The Pages workflow writes `frontend/config.js` during deployment and publishes the static site. It fails early if a required variable is missing. The public anon key is expected to be visible in the browser; never put a database password, Supabase service-role key, or LLM key in frontend variables.

### 4. Check the live flow

Open the Pages URL, create an account, confirm the email if Supabase requires it, sign in, upload a text-based PDF or DOCX, search and inspect ranked roles, generate a kit, save a role, change its tracker status, export CSV, then try Delete my resume and application data. Test with a sample resume first.

## Before the first push

The current local `apple-redesign` branch contains commits not present on GitHub `main`. Inspect and merge those changes intentionally. A local version of `backend/.env.example` previously contained credential-shaped Supabase/database values; the working copy now replaces them with placeholders, but the old values remain in the unpushed Git commit history until that history is rewritten. Rotate the database password and Supabase secret key in the Supabase dashboard, then rewrite/squash the unpushed commits so the old values are absent from every commit before pushing. Never copy those values into Render, GitHub, or chat.

## Development commands

```bash
cd backend
alembic upgrade head
pytest
ruff check .
ruff format --check .
mypy app
```

CI runs migrations, backend tests, lint, formatting, and type checking on pushes and pull requests to `main`.
