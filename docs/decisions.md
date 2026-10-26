# Architecture Decision Records

## ADR-001: Python 3.12
**Status:** Accepted  
**Date:** 2025-10-25  
**Decision:** Pin Python to 3.12 (< 3.13)  
**Rationale:** ML libraries lack reliable wheels on Python 3.14.

## ADR-002: Public ATS APIs over scraping
**Status:** Accepted  
**Date:** 2025-10-25  
**Decision:** Use public APIs and ATS JSON endpoints only (Greenhouse, Lever, Ashby, Adzuna, RemoteOK, custom career pages). No scraping of LinkedIn/Naukri/Indeed.  
**Rationale:** Legal/ToS compliance and reliability.

## ADR-003: RAG strategy
**Status:** Accepted  
**Date:** 2025-10-25  
**Decision:** Use RAG for job retrieval and tailor grounding, but NOT for resume parsing.  
**Rationale:** Resume fits in context; RAG adds complexity without benefit for parsing.

## ADR-004: No auto-submit
**Status:** Accepted  
**Date:** 2025-10-25  
**Decision:** Public app will not auto-submit applications.  
**Rationale:** User control and ToS compliance.

## ADR-005: Privacy-first processing
**Status:** Accepted  
**Date:** 2025-10-25  
**Decision:** Process resumes in memory, delete after TTL, never log resume text.  
**Rationale:** Privacy and compliance.

## ADR-006: Supabase Postgres instead of SQLite/Cloudinary
**Status:** Accepted  
**Date:** 2025-10-25  
**Decision:** Use Supabase Postgres (via SQLAlchemy async + Alembic) for all user data, replacing SQLite. Use Supabase Storage private bucket with signed URLs for file storage, replacing Cloudinary.  
**Rationale:** Production deployment on Render free tier (512 MB RAM) requires a managed Postgres and object storage. SQLite does not support concurrent access on Render. Row Level Security (RLS) policies scoped to `auth.uid()` enforce per-user data isolation at the database level.

## ADR-007: Hosted embeddings / reranker for 512 MB limit
**Status:** Accepted  
**Date:** 2025-10-25  
**Decision:** No torch, sentence-transformers, or cross-encoder in the production image. Use hosted embeddings API (or fastembed ONNX) behind an `Embedder` interface, and a hosted reranker behind a `Reranker` interface. Both have fake implementations for tests. Heavier models are allowed in offline `evals/` only.  
**Rationale:** Render free tier has 512 MB RAM; ML libraries exceed this limit.

## ADR-008: HashRouter for GitHub Pages
**Status:** Accepted  
**Date:** 2025-10-25  
**Decision:** Frontend uses React + Vite + TypeScript with HashRouter, deployed to GitHub Pages via GitHub Actions. Vite `base` set to repo name. API URL and Supabase public keys read from build-time env vars.  
**Rationale:** GitHub Pages serves static files from a subdirectory; HashRouter avoids server-side routing issues.

## ADR-006: SSE over WebSockets
**Status:** Accepted  
**Date:** 2025-10-26  
**Decision:** Use Server-Sent Events (SSE) for pipeline live visualization.  
**Rationale:** Simpler one-way streaming, easier to work with HTTP/proxies, supports auto-reconnect, and auth via headers with fetch-event-source.
