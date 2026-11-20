# ShellSathi — Project Overview & Architecture

## 1. Executive Summary

**ShellSathi** is an intelligent, production-ready Linux command assistant developed by **Harsh Vilas Aher** (Roll No: `2125PCAM1004`, Project ID: `SJ-62`) as part of the **Sanjivani AI to GenAI Engineer Training Program**.

The project addresses the core challenge beginners face when navigating the Linux command line: remembering syntax, flags, destructive command safety, and octal/symbolic permission conversions. ShellSathi combines:
1. **Interactive Command Catalog & CLI** (Day 1–2): Structured metadata and local search.
2. **Automated TLDR Markdown Ingestion** (Day 3): Scraping and parsing official command documentation.
3. **Lexical Search (TF-IDF)** (Day 4): Cosine similarity and keyword scoring.
4. **Safety Boundaries & Out-of-Scope Detection** (Day 5): Guardrails against non-Linux queries.
5. **Multi-Provider LLM Integration** (Day 6): Structured JSON responses with fallback logic.
6. **Dense Neural Semantic Search** (Day 7): ChromaDB vector embeddings (`all-MiniLM-L6-v2`).
7. **Retrieval-Augmented Generation (RAG)** (Day 8): Context retrieval with verified markdown citations.
8. **Stateful LangGraph Autonomous Agent** (Day 9): Multi-step execution, `chmod` conversions, safety approval gates, and session memory.
9. **Interactive Streamlit Web Interface** (Day 10): Dual-mode chat (Ask / Agent), command placeholder filler, and user feedback collection.
10. **Containerized Docker Deployment** (Day 11): Multi-service Dockerfile and Docker Compose orchestration.
11. **Continuous Integration & Cloud Deployment** (Day 12): Automated GitHub Actions CI workflow, Ruff linting, Pytest test suite, and Render deployment blueprint.

---

## 2. Unified Repository Architecture

```text
ShellSathi/
│
├── .github/
│   └── workflows/
│       └── ci.yml               # Automated GitHub Actions CI pipeline
│
├── app/
│   ├── __init__.py              # Python package initializer
│   ├── main.py                  # FastAPI REST API application
│   ├── cli.py                   # Interactive console CLI interface
│   ├── records.py               # Command catalog loader, filtering and search
│   ├── models.py                # Dataclasses and Pydantic request/response schemas
│   ├── ingest.py                # Markdown parser and structured data ingestion
│   ├── fetch.py                 # Remote TLDR markdown dataset fetcher
│   ├── smart_search.py          # TF-IDF vectorizer and cosine similarity search
│   ├── chunking.py              # Text chunker preserving source/page/title metadata
│   ├── embed.py                 # Dense neural embedding generator (ONNX runtime)
│   ├── vectorstore.py           # Persistent Chroma vector database manager
│   ├── rag.py                   # Retrieval-Augmented Generation retrieval and synthesis
│   ├── llm.py                   # Multi-provider LLM abstraction (Groq, Gemini, Fake)
│   ├── tools.py                 # chmod bi-directional calculator & safety verification
│   ├── agent_loop.py            # Simple autonomous tool-calling agent loop
│   ├── graph.py                 # Stateful LangGraph agent with MemorySaver & approval
│   └── placeholder.py           # Signature interactive command placeholder filler
│
├── ui/
│   └── app.py                   # Streamlit web application with Ask/Agent modes
│
├── data/
│   ├── raw/                     # Original TLDR markdown source files (ls, grep, tar, chmod)
│   ├── processed/               # Standardized records and data exports
│   ├── chroma_db/               # Persistent Chroma neural vector index
│   ├── feedback.json            # User feedback ratings and logs
│   └── records.json             # Master dataset of 20 core Linux commands
│
├── analysis/
│   └── explore.py               # Exploratory data analysis (pandas statistics)
│
├── docs/
│   ├── project_overview.md      # This comprehensive architecture overview
│   ├── how_llms_work.md         # In-depth LLM fundamentals documentation
│   ├── screenshots/             # Streamlit UI & placeholder filler screenshots
│   └── history/                 # Preserved early assignment scripts (Day 1-2)
│       ├── day01_intro.py       # Day 1 project card script
│       ├── day01_menu.py        # Day 1 basic menu script
│       └── sample_records.py    # Day 2 initial python records catalog
│
├── prompts/
│   ├── system_prompt.txt        # System prompt with strict Linux boundaries
│   └── eval_prompt.txt          # Evaluation prompt template
│
├── eval/
│   ├── baseline_results.json    # Initial search benchmarks
│   ├── context_results.json     # Context augmentation results
│   ├── eval_dataset.json        # 10 standard evaluation questions
│   ├── eval_summary.md          # Comprehensive evaluation report
│   ├── feedback_log.json        # User ratings and feedback storage
│   ├── latency_comparison.png   # Latency comparison visual chart
│   ├── rag_results.json         # RAG evaluation results
│   ├── run_eval.py              # Benchmark execution script
│   ├── search_results.md        # Semantic vs lexical comparison
│   └── vector_benchmark.json    # Vector search benchmark data
│
├── tests/
│   ├── conftest.py              # FastAPI TestClient & mock LLM fixtures
│   ├── test_records.py          # Command catalog unit tests
│   ├── test_search.py           # TF-IDF & Chroma vector search tests
│   ├── test_api.py              # FastAPI endpoints & validations
│   ├── test_tools.py            # chmod calculator & safety checks
│   ├── test_agent.py            # LangGraph agent memory & approval tests
│   ├── test_day10.py            # UI helpers & placeholder filler tests
│   └── test_all_days.py         # Full Day 1–10 regression test suite
│
├── .dockerignore                 # Docker build exclusions
├── .env.example                 # Template for API keys and configuration
├── .gitignore                   # Git exclusions (caches, credentials, venv)
├── docker-compose.yml           # Multi-container orchestration (FastAPI + Streamlit)
├── Dockerfile                   # Multi-service production container specification
├── pyproject.toml               # Tool configuration (Ruff, Pytest with pythonpath)
├── render.yaml                  # Render Infrastructure-as-Code Blueprint
├── requirements.txt             # Production and test dependencies
└── README.md                    # Complete project documentation & CI badge
```

---

## 3. Component Interactions & Data Flow

```text
   +-------------------------------------------------------------------+
   |              Streamlit User Interface (ui/app.py)                 |
   |   • Mode 1: Ask (RAG with citations)                              |
   |   • Mode 2: Agent (LangGraph with tool calls & approvals)         |
   |   • Signature Feature: Dynamic Interactive Placeholder Filler     |
   |   • Feedback Collection: Thumbs Up / Down ratings                 |
   +-------------------------------------------------------------------+
                                    │
                                    ▼ HTTP REST Requests
   +-------------------------------------------------------------------+
   |                   FastAPI Backend (app/main.py)                   |
   |   • POST /ask       • POST /agent       • POST /feedback          |
   |   • GET /health     • GET /records      • GET /search/semantic    |
   +-------------------------------------------------------------------+
             │                                       │
             ▼                                       ▼
   +--------------------+                 +--------------------+
   |   RAG Subsystem    |                 |  LangGraph Agent   |
   |   (app/rag.py)     |                 |  (app/graph.py)    |
   +--------------------+                 +--------------------+
             │                                       │
     +-------+-------+                       +-------+-------+
     │               │                       │               │
     ▼               ▼                       ▼               ▼
+----------+   +-----------+          +-------------+  +-------------+
| ChromaDB |   | LLM Client|          | chmod Tools |  | Human Gate  |
| (Dense)  |   | (app/llm) |          | (app/tools) |  | (Approval)  |
+----------+   +-----------+          +-------------+  +-------------+
```

---

## 4. Training Milestones Summary (Day 1 to Day 12)

| Phase | Milestone | Key Deliverables |
|---|---|---|
| **Week 1** (Day 1–5) | Catalog, CLI & Ingestion | `app/records.py`, `app/cli.py`, `app/ingest.py`, `app/smart_search.py`, `data/records.json` |
| **Week 2** (Day 6–7) | LLM, ONNX & Vectorstore | `app/llm.py`, `app/chunking.py`, `app/embed.py`, `app/vectorstore.py`, ChromaDB |
| **Week 2** (Day 8–9) | RAG & LangGraph Agent | `app/rag.py`, `app/tools.py`, `app/agent_loop.py`, `app/graph.py` |
| **Week 2** (Day 10) | Streamlit UI & Signature Filler | `ui/app.py`, `app/placeholder.py`, `POST /feedback` |
| **Week 3** (Day 11) | Pytest Suite & Docker | 76 automated tests, `Dockerfile`, `docker-compose.yml` |
| **Week 3** (Day 12) | CI/CD & Project Organization | `.github/workflows/ci.yml`, `render.yaml`, unified architecture |
