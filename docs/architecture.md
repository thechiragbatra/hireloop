# Architecture

Hireloop is a static browser app backed by a FastAPI service.

## Request flow

```mermaid
flowchart LR
    A[Browser sign-in] -->|Supabase access token| B[FastAPI]
    B --> C[Parse PDF/DOCX]
    C --> D[Store profile facts]
    D --> E[Fetch public job feeds]
    E --> F[Rank jobs against profile]
    F --> G[Draft cited resume bullets]
    G --> H[Check source support]
    H --> I[Save or track application]
```

The browser obtains email/password or Google OAuth sessions from Supabase Auth. Protected API routes verify the bearer token and use its `sub` claim as the owner ID. Public job listings are cached as shared records. Profile and application records are stored in the `hireloop_records` table with an owner ID and JSON payload.

The original resume file and extracted full text are not retained. Structured profile facts are retained so the user can match jobs and generate drafts. The user can erase their profile and application records through the app.

## Components

- **Frontend:** static HTML/CSS/JavaScript, deployed to GitHub Pages. Runtime configuration is written by the Pages workflow.
- **API:** FastAPI, deployed to Render. SQLAlchemy uses SQLite for local development and Postgres for production.
- **Database schema:** Alembic migration `0001_create_records` creates the profile/job/application record table.
- **Authentication:** Supabase Auth in the browser; API JWT validation through Supabase JWKS (or a legacy HS256 JWT secret).
- **Resume parsing:** `pypdf` and `python-docx`, with heuristic extraction for common headings and skill terms. Image-only PDF OCR is not included.
- **Job sources:** Remote OK, We Work Remotely, Jobicy, and Himalayas public feeds. Provider failures are isolated so one unavailable source does not fail the whole search.
- **Matching and tailoring:** deterministic keyword/skill scoring and source-copying drafts work without an LLM key. A configured OpenRouter-compatible model can provide richer ranking and rewrites; generated output is checked against profile evidence.

## Privacy boundary

Production startup requires a database and Supabase token-verification configuration. The API enforces owner filters for profile and application operations. Database-level Supabase RLS policies are not installed by this project; production access to the database must remain server-side.

Resume text must not be logged. If an LLM key is configured, relevant profile and job text is sent to that provider for model-assisted features. The API key stays in the backend environment.

## Deferred work

- OCR for scanned resumes and richer structured experience/company/date extraction.
- Live streaming pipeline progress; the current UI performs discrete requests and does not depend on SSE.
- Database-level RLS policies, account-deletion integration with Supabase Auth, and automated retention expiry.
- More job providers, deduplication across changing feed identifiers, and an evaluation set for ranking quality.
