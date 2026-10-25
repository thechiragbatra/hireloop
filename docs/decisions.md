# Architecture Decision Records

## ADR-001: Python 3.12
**Status:** Accepted  
**Date:** 2025-10-25  
**Decision:** Pin Python to 3.12 (< 3.13)  
**Rationale:** ML libraries (torch, sentence-transformers, faiss) lack reliable wheels on Python 3.14.

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
