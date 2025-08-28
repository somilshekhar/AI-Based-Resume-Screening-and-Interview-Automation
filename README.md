
# AI-Based Resume Screening & Interview Automation — Full Project Scaffold

This scaffold implements a production-oriented architecture and codebase to meet the technical
assessment's requirements. It's a deployable starting point — not a drop-in finished SaaS — but it
includes all major components, integration points, and sample implementations to demonstrate
how the full system would operate.

## Architecture Overview
- **api/** - FastAPI gateway and orchestration layer (exposes REST API)
- **parser_service/** - Resume parsing microservice (PDF/DOCX/OCR, NER via spaCy)
- **ranking_service/** - Candidate ranking microservice (embeddings, semantic matching, scoring)
- **scheduler_service/** - Interview scheduling microservice (calendar integrations)
- **fairness/** - Bias detection & monitoring utilities
- **audit/** - Immutable audit logger (writes decision logs to DB + append-only files)
- **infra/** - Dockerfiles, docker-compose, and deployment helpers
- **migrations/** - Database migration stubs (alembic)
- **sample_data/** - sample resumes and job descriptions

## What this scaffold provides
- Resume extraction with PDF/DOCX/OCR fallback
- NER-based entity extraction (spaCy)
- Embeddings-based semantic matching (sentence-transformers)
- Scoring pipeline (skill match, experience match, education match, cultural fit heuristic)
- Summarization template + placeholder for LLM integration (OpenAI/Anthropic)
- Scheduler with Google Calendar integration placeholders and OAuth flow notes
- Fairness utilities: demographic parity, equalized odds computation, anonymization pipeline
- Audit logging + model versioning stubs
- Docker Compose for local multi-service testing
- CI/CD example (GitHub Actions) to run tests and linting
- README with roadmap and extension plan to reach enterprise-scale (50k resumes/month, 1000+/min)

## How to run (local dev)
1. Install dependencies (use a virtual env):
   ```bash
   pip install -r requirements.txt
   ```
2. Start services with docker-compose (requires Docker & docker-compose)
   ```bash
   cd infra && docker-compose up --build
   ```
3. Or run api directly (for quick dev):
   ```bash
   uvicorn api.main:app --reload --port 8000
   ```

## Notes for the Interview
- This scaffold demonstrates domain knowledge across parsing, ranking, fairness, scheduling, and auditability.
- For the interview/demo: run the API locally, show parsing + ranking for sample resumes, present fairness dashboard metrics (CSV/console), and walk through the roadmap for production scaling.

