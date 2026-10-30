# Privacy

Hireloop processes resumes to create a profile, find jobs, draft tailored materials, and track applications.

- The original uploaded file is processed in memory and is not written to the database or object storage by this version.
- The parsed profile, including contact details and resume facts, and application records are stored in the configured database. Production API access requires a valid Supabase access token; records are scoped to the token subject.
- Job listings are public provider data and are cached as shared records.
- Resume contents are not written to application logs. Do not enable resume-text logging.
- Model-assisted features send relevant profile/job text to the LLM provider configured by the operator. Keep the key server-side and review that provider’s data terms before enabling this feature. With no key, matching and resume tailoring use the local factual fallback.
- Generated materials are drafts for user review. Hireloop does not submit applications.
- Use “Delete my resume and application data” to erase stored profile and application records. This does not delete the Supabase login itself; delete the login separately in Supabase Auth if needed.

Production deployment requires the operator to use a protected Postgres connection and configure Supabase Auth. The application currently enforces ownership in its API layer; it does not configure database-level Supabase RLS policies.
