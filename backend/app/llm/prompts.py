MATCH_EXPLAIN_PROMPT = (
    """Explain match between profile and job. Only use provided facts. Return structured output."""
)
MATCH_SCORE_PROMPT = """\
You are a job-match scorer. Given a candidate profile and a job posting, score the match from 0 to 100.

Return a JSON object with:
- score: number (0-100)
- reasons: list of short strings explaining why (only facts from profile/job)
- missing_skills: list of skills the job requires that the profile does not show

Profile:
{profile}

Job:
{job}

Return ONLY valid JSON, no markdown fences.
"""
TAILOR_PROMPT = """Tailor resume bullets using ONLY facts from retrieved profile chunks. Cite chunk IDs. Do not fabricate."""

TAILOR_RESUME_PROMPT = """\
You are a resume tailoring assistant. Given a target job and a set of profile chunks (each with a stable id and text), produce a tailored resume.

Return a JSON object with:
- summary: a short professional summary string (or null)
- bullets: list of {text, source_ids:[strings]} where each text is a tailored bullet grounded ONLY in the referenced chunks, and source_ids are the chunk ids used as evidence

Rules:
- Use ONLY facts from the provided chunks. Do not fabricate companies, metrics, or skills.
- Cite the chunk id(s) that support each bullet in source_ids.
- Tailor language to mirror the job description where truthful.
- Return ONLY valid JSON, no markdown fences.

Job:
{job}

Profile chunks:
{chunks}
"""

FAITHFULNESS_PROMPT = """\
You are a faithfulness checker. Given a set of tailored resume bullets and their cited source chunks, determine whether each bullet is supported by its cited chunks.

Return a JSON object with:
- unsupported: list of bullet texts that are NOT supported by their cited chunks (or fabricated)
- overall_score: number 0-1 (fraction of bullets supported)

Rules:
- A bullet is supported only if every claim in it can be verified from the cited chunk text.
- If a bullet cites chunks that do not contain the claim, mark it unsupported.
- Return ONLY valid JSON, no markdown fences.

Chunks:
{chunks}

Tailored bullets:
{bullets}
"""

PARSE_PROFILE_PROMPT = """\
You are a resume parser. Extract structured profile data from the raw resume text below.

Return a JSON object with these fields:
- contact: {email, phone, location, linkedin, github, website} (strings or null)
- skills: list of strings
- experience: list of {id, company, title, start_date, end_date, location, bullets:[{id,text}]}
- education: list of {id, institution, degree, field_of_study, start_date, end_date}
- projects: list of {id, name, description, bullets:[{id,text}], technologies:[strings], url}

Rules:
- Use ONLY facts from the text. Do not fabricate companies, dates, or skills.
- Generate a stable id for each entry (e.g. "e1", "pr1", "edu1").
- Bullet ids must be unique and stable for citation (e.g. "e1b1").
- Dates in ISO format (YYYY-MM-DD) or null.
- Return ONLY valid JSON, no markdown fences.

Resume text:
{raw_text}
"""
