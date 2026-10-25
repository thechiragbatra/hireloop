# Privacy Policy

## Data Ownership
- All user data (profiles, jobs, applications, tailored resumes) is scoped to the authenticated user via `user_id`.
- Row Level Security (RLS) policies on every table enforce isolation at the database level, scoped to `auth.uid()`.
- Users can only access their own data.

## File Storage
- Uploaded resumes and generated cover letters are stored in a private Supabase Storage bucket.
- Files are accessed via signed URLs only (time-limited, revocable).
- No public read access to stored files.

## Data Retention & Deletion
- Raw resume text is processed in memory and retained per `RESUME_TTL_SECONDS` (default 3600 seconds).
- A TTL deletion job removes raw files after the TTL expires.
- Users can request full account and data deletion via `DELETE /api/v1/tracker/account`, which removes all profiles, jobs, applications, and stored files for that user.
- Data is never logged. Only IDs, sizes, and timings are logged (never resume text or profile content).

## Third-Party Services
- No scraping of LinkedIn, Naukri, or Indeed. Only public ATS APIs are used.
- Bring-your-own LLM key supported; shared keys are rate-limited by IP.
- Supabase Auth handles authentication (email + Google). The service-role key exists only in backend environment variables.
