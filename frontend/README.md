# Hireloop Frontend

React + TypeScript + Vite + Tailwind SPA for the Hireloop AI Job Copilot.

## Tech stack

- React 19 + TypeScript
- Vite (build tool)
- Tailwind CSS (styling)
- React Router (hash-based routing for GitHub Pages SPA compatibility)
- Supabase JS client (auth + storage)
- Axios (API client with Supabase JWT interceptors)
- Lucide React (icons)

## Pages

| Path | Purpose |
|------|---------|
| `/login` | Sign in / sign up (email, Google OAuth) |
| `/dashboard` | Onboarding: upload resume, find jobs, track applications |
| `/upload` | Upload and parse resume (PDF/DOCX) |
| `/jobs` | Browse jobs from public ATS sources |
| `/match` | Match score details for a job |
| `/tailor` | Tailor resume with faithfulness report |
| `/tracker` | Application tracker |
| `/apply-kit/:profileId/:jobId` | Download tailored resume + cover letter |

## Setup

```bash
cd frontend
npm install

# Environment (copy .env.example to .env.local and fill in values)
cp .env.example .env.local

# Dev server (proxies /api to backend)
npm run dev          # http://localhost:5173

# Production build for GitHub Pages (base path /hireloop-1/)
VITE_BASE=/hireloop-1/ npm run build   # output: frontend/dist/

# Preview production build locally
npm run preview
```

## GitHub Pages deployment

Deploys automatically on push to `main` via `.github/workflows/frontend.yml`. Requires repo secrets:

- `VITE_API_URL` — Render backend URL
- `VITE_SUPABASE_URL` — Supabase project URL
- `VITE_SUPABASE_ANON_KEY` — Supabase anon key

## Notes

- Uses `HashRouter` so the SPA works on GitHub Pages without a `404.html` fallback.
- `vite.config.ts` sets `base` from `VITE_BASE` (defaults to `/hireloop-1/`).
- Auth tokens are stored in `localStorage` and attached to Axios requests as `Authorization: Bearer <token>`.
