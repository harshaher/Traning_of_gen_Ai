# ShellSathi – Project Progress Tracking (Day 1 to Day 14)

**Student Name:** Harsh Vilas Aher  
**Roll Number:** 2125PCAM1004 | **Project ID:** SJ-62  
**Training Program:** Sanjivani AI Training – AI to GenAI Engineer  

---

## Milestone Status Summary

- **Total Milestones:** 14 Days + Final Demo
- **Completed Milestones:** 13 / 14 Complete (Technical implementation, tests, CI/CD, documentation)
- **Open / In-Progress Items:** 2 (Render Live Cloud URL activation, Student Personal Demo Rehearsal)

---

## Detailed Milestone Checklist

### Day 1: Project Initiation & CLI Prototype
- [x] Define product vision, user persona, and problem statement (`docs/history/day01_intro.py`).
- [x] Implement initial interactive console menu and rule check (`docs/history/day01_menu.py`).
- [x] Initial dataset prototype of core Linux commands (`docs/history/sample_records.py`).

### Day 2: Command Records & Dataset Schema
- [x] Master dataset of 20 core Linux commands created (`data/records.json`).
- [x] Category classifications and destructive command tagging (`app/records.py`).
- [x] Interactive CLI for browsing and searching catalog (`app/cli.py`).
- [x] Automated unit tests for records loading, filtering, and categories (`tests/test_records.py`).

### Day 3: Ingestion Pipeline & Dataclass Models
- [x] Structured `Record` dataclass model (`app/models.py`).
- [x] Raw TLDR Markdown file downloader (`app/fetch.py`).
- [x] Markdown ingestion parser targeting task descriptions and syntax (`app/ingest.py`).
- [x] Filter out multilingual mirrors (`pages.hi`, `pages.mr`) and platform duplicates (`pages/osx`, `pages/windows`).

### Day 4: TF-IDF Smart Search & FastAPI Base Endpoints
- [x] TF-IDF lexical retrieval engine with cosine scoring and keyword boosting (`app/smart_search.py`).
- [x] FastAPI web application initialization (`app/main.py`).
- [x] REST endpoints: `GET /health`, `GET /records`, `GET /records/{id}`, `GET /search`, `POST /questions`.
- [x] Unit and API integration tests (`tests/test_search.py`, `tests/test_api.py`).

### Day 5: Out-of-Scope Detection & Safety Boundaries
- [x] Scope boundary classifier for non-Linux queries (`app/rag.py:is_out_of_scope`).
- [x] Standard refusal response for queries outside Linux command documentation.
- [x] Boundary regression tests covering out-of-scope questions (`tests/test_all_days.py`).

### Day 6: LLM Chat Integration with Structured Schema
- [x] Multi-provider LLM client supporting Groq LLaMA-3.3 and Google Gemini (`app/llm.py`).
- [x] Structured JSON schema enforcing `answer`, `confidence`, `follow_up` (`app/models.py`).
- [x] REST endpoint: `POST /chat`.
- [x] Offline heuristic fallback generator for deterministic testing.

### Day 7: Dense Semantic Search via ChromaDB
- [x] Persistent ChromaDB vector database manager (`app/vectorstore.py`).
- [x] 384-dimensional dense neural embeddings using `all-MiniLM-L6-v2` (`app/embed.py`).
- [x] Pre-computed index of 44 document chunks (`data/chroma_db/`).
- [x] REST endpoint: `GET /search/semantic`.

### Day 8: Full RAG Pipeline & Evaluation Benchmark
- [x] Retrieval-Augmented Generation pipeline (`app/rag.py:answer_with_rag`).
- [x] Relevance threshold filtering (`0.35`) to prevent hallucinated answers.
- [x] Verified Markdown source citations pointing to indexed documentation.
- [x] REST endpoint: `POST /ask`.
- [x] Automated RAG evaluation benchmark across 15 test queries (`eval/run_eval.py`, `eval/rag_compare.md`).

### Day 9: Autonomous Agent with Tools & LangGraph
- [x] Deterministic bi-directional `chmod_calculator` tool (`app/tools.py`).
- [x] Safety analyzer detecting destructive commands (`rm -rf`, `dd`, `mkfs`, `kill -9`, `chmod 777`).
- [x] 6-node stateful LangGraph agent with `MemorySaver` thread isolation (`app/graph.py`).
- [x] Human-in-the-loop approval gate via `interrupt()` for hazardous actions.
- [x] REST endpoint: `POST /agent`.

### Day 10: Streamlit UI & Interactive Placeholder Filler
- [x] Modern dual-mode Streamlit web application (`ui/app.py`).
- [x] Dynamic command placeholder parser and interactive input forms (`app/placeholder.py`).
- [x] Thumbs up/down feedback collection and persistent storage (`POST /feedback`, `data/feedback.json`).
- [x] Backend connectivity health monitoring and thread memory management.

### Day 11: Testing, Quality, Docker & Containerization
- [x] Complete automated test suite of 88 passing tests (`pytest -v`).
- [x] Zero code style and linting errors (`ruff check .`, `ruff format --check .`).
- [x] Multi-service `Dockerfile` targeting `linux/amd64` architecture.
- [x] Multi-container orchestration linking API and UI services (`docker-compose.yml`).

### Day 12: CI/CD & Project Architecture Unification
- [x] Automated GitHub Actions continuous integration workflow (`.github/workflows/ci.yml`).
- [x] Unified repository structure eliminating daily fragmented folders.
- [x] Infrastructure-as-Code deployment blueprint for Render cloud (`render.yaml`).

### Day 13: Production Readiness & Hardening (S1 & S2)
- [x] Request latency logging ASGI middleware (`X-Request-ID`, `X-Process-Time-Ms`).
- [x] Cross-Origin Resource Sharing (`CORSMiddleware`) enabled for production frontend access.
- [x] In-memory thread-safe `ResponseCache` yielding 45.4x latency speedup (593ms to 13ms).
- [x] Real-time token usage telemetry across LLM providers.
- [x] Defense-in-depth input sanitization (500-char cap, `top_k` bounds 1–10, upload validation).

### Day 14: Interview Documentation, Auditing & Final Delivery
- [x] Technical interview documentation created (`docs/interview.md`):
  - 60-second project pitch.
  - Answers to 10 likely technical and project interview questions.
  - Technical deep-dive on TLDR chunking challenge.
  - Placeholders and `[c]reate` syntax explanation.
  - Translated folder (`pages.hi`, `pages.mr`) and platform duplicate filtering.
  - Destructive command safety warnings (`rm -rf`, `dd`, `mkfs`, `chmod 777`).
- [x] Bytecode compilation clean (`python -m compileall app ui tests`).
- [x] Linter and formatter clean (`ruff check .`, `ruff format --check .`).
- [x] All 88 automated tests passing (`pytest -v`).
- [x] Dependency check verified (`pip check` with 0 broken requirements).
- [x] Docker Compose configuration validated (`docker compose config`).
- [ ] **Open Item 1: Render Live Deployment Activation** – Blueprint (`render.yaml`) and Docker image instructions prepared. Activation depends on student applying blueprint on their personal Render dashboard.
- [ ] **Open Item 2: Final Demo Rehearsal** – The student must personally rehearse the 5-minute project demo twice before final presentation.
