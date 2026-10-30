# Failure Analysis

| Date | Symptom | Root Cause | Fix |
|------|---------|------------|-----|
| 2026-10-26 | GitHub CI stopped before backend tests | Workflow ran `alembic upgrade head`, but no Alembic config or migration existed | Add `alembic.ini`, migration environment, and initial records-table migration |
