# Hireloop - AI Job Copilot

**Status:** Under construction

An AI-powered job copilot that helps job seekers find matching jobs, tailor resumes honestly with faithfulness checks, and track applications.

## Setup

### Prerequisites
- Python 3.12
- Node.js (for frontend, coming soon)

### Backend Setup
```bash
# Create virtual environment with Python 3.12
python3.12 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
cd backend
pip install -e ".[dev]"
```

### Environment
Copy `.env.example` to `.env` and fill in your values. Never commit `.env`.

### Running
```bash
make run
# or
cd backend && uvicorn app.main:app --reload
```

## Features (Planned)
- Resume parsing (PDF/DOCX)
- Job matching from public ATS APIs
- Honest resume tailoring with faithfulness verification
- Application tracker
- Privacy-first processing

## Privacy
See [PRIVACY.md](PRIVACY.md) for details.
