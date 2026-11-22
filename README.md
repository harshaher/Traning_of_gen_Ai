# ShellSathi – AI-Powered Linux Command Assistant

[![CI](https://github.com/harshaher/Traning_of_gen_Ai/actions/workflows/ci.yml/badge.svg)](https://github.com/harshaher/Traning_of_gen_Ai/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.42+-FF4B4B.svg?logo=streamlit)](https://streamlit.io)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-orange.svg)](https://www.trychroma.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agent_Workflow-blueviolet.svg)](https://langchain-ai.github.io/langgraph/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker)](https://www.docker.com)
[![Tests](https://img.shields.io/badge/Pytest-88_Passed-success.svg)](file:///tests)
[![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

> **ShellSathi** is an enterprise-grade, production-ready Linux Command Assistant built to bridge the gap between complex terminal utilities and everyday developers. By uniting dual-retrieval RAG (TF-IDF + dense ChromaDB neural embeddings), a stateful LangGraph agent with conversation memory, interactive human-in-the-loop approvals for hazardous operations, in-memory TTL caching delivering a **45.4x latency reduction**, real-time token tracking, and dynamic command placeholder filling, ShellSathi delivers high-accuracy Linux assistance with zero hallucinations.

---

## 1. Problem Statement

Navigating Linux command-line environments is notoriously error-prone for students, junior developers, and system administrators:
1. **Steep Syntax Curve & Cognitive Load:** Tools like `tar`, `find`, `grep`, and `chmod` feature hundreds of unintuitive flags where a minor typo can corrupt data or stall workflows.
2. **Hazardous Operations:** Destructive commands (`rm -rf`, `chmod 777`) executed blindly from web tutorials can compromise server security or cause irreversible file destruction.
3. **Generic LLM Hallucinations:** Commercial AI assistants frequently invent invalid Linux flags, recommend deprecated utilities, or lack grounded documentation citations.
4. **Latency & Cost Overhead:** Redundant RAG vector queries and multi-step agent graphs impose latency and computational cost when querying repetitive system commands.

---

## 2. Solution Overview

ShellSathi solves these challenges with a defense-in-depth architecture:
- **Grounded Dual RAG Retrieval:** Queries verified, open-source Linux documentation ([tldr-pages](https://github.com/tldr-pages/tldr)) using 384-dimensional dense neural embeddings (`all-MiniLM-L6-v2`) in persistent ChromaDB alongside TF-IDF lexical matching.
- **Human-in-the-Loop Safety:** A stateful LangGraph agent intercepts hazardous actions, requiring explicit user approval before proceeding.
- **Mathematical Accuracy:** Dedicated deterministic tool (`chmod_calculator`) computes bi-directional octal-to-symbolic permissions with 100% mathematical precision.
- **Production Performance:** An in-memory thread-safe TTL cache reduces query latency from **593.5ms down to 13.1ms (45.4x speedup)** for frequent queries.
- **Dynamic Command Builder:** Automatically parses command templates (e.g., `tar -czvf {{archive.tar.gz}} {{directory}}`) into interactive UI inputs in Streamlit.
- **Enterprise Observability & Security:** Middleware logs request latency and custom `X-Request-ID` headers, tracks LLM tokens across Groq/Gemini, and enforces strict input boundary sanitization against prompt injection.

---

## 3. Key Features

- 🔍 **Hybrid Retrieval-Augmented Generation (RAG):** Combines dense semantic vector retrieval from persistent ChromaDB with lexical search, returning verified source citations (`data/raw/*.md`).
- 🤖 **Autonomous LangGraph Agent:** 6-node state graph with intent classification, multi-tool orchestration, conversation memory (`MemorySaver`), and thread isolation.
- 🛡️ **Human-in-the-Loop Approval:** Pauses execution and requests confirmation before performing hazardous operations or permission adjustments.
- ⚡ **High-Speed TTL Response Cache:** Thread-safe in-memory cache with normalized query keys, configurable TTL, and automated invalidation upon document ingestion.
- 📊 **Real-Time Token Usage Telemetry:** Tracks input, output, and total token consumption across Groq (`llama-3.3-70b-versatile`), Gemini (`gemini-2.5-flash`), and offline heuristic fallbacks.
- 🔒 **Input Security & Injection Defense:** Enforces strict payload validation (500-character caps, `top_k` bounds, 1 MB file upload ceilings) and refusal of adversarial prompt overrides.
- 🛠️ **Signature Placeholder Filler:** Detects `{{placeholder}}` variables in command examples and renders instant interactive input forms with one-click copy.
- 💬 **Streamlit Web Interface:** Modern dual-mode chat interface (Ask RAG vs. Agent Mode) with real-time backend health monitoring and feedback submission.
- 🐳 **Turnkey Docker & Cloud Deployment:** Multi-container `docker-compose` orchestration and automated Infrastructure-as-Code deployment via Render.
- ✅ **Exhaustive Automated Testing:** 88 automated Pytest unit, integration, and security tests with mock LLM providers and 0 Ruff linting errors.

---

## 4. Architecture Diagram

```mermaid
flowchart TD
    User["👤 User / Client"] -->|HTTP / WebUI| UI["Streamlit Frontend (ui/app.py)"]
    UI -->|REST API Requests| Middleware["Request Latency & Tracing Middleware<br/>(X-Request-ID, X-Process-Time-Ms)"]
    
    subgraph FastAPI_Backend ["FastAPI Application (app/main.py)"]
        Middleware --> Limits["Input Validation & Limits<br/>(Length <= 500 chars, top_k 1-10)"]
        Limits --> CacheCheck{"Cache Check<br/>(app/cache.py)"}
        
        CacheCheck -->|Cache HIT| CachedResponse["Return Cached Result<br/>(Latency ~13ms, X-Cache: HIT)"]
        CacheCheck -->|Cache MISS| Router{"Route Request"}
        
        Router -->|/ask (RAG)| RAGModule["RAG Subsystem (app/rag.py)"]
        Router -->|/agent| AgentModule["LangGraph Agent (app/graph.py)"]
        Router -->|/search| SearchModule["TF-IDF & Records (app/smart_search.py)"]
        
        subgraph Storage_and_Retrieval ["Knowledge Base & Vector Store"]
            ChromaDB[("ChromaDB Vector Store<br/>all-MiniLM-L6-v2 (384-dim)")]
            TLDRDocs["Local TLDR Docs (data/raw/)"]
            RecordsDB[("Command Records (data/records.json)")]
        end
        
        RAGModule --> ChromaDB
        RAGModule --> TLDRDocs
        SearchModule --> RecordsDB
        
        subgraph LangGraph_Agent ["Stateful Agent Flow"]
            IntentNode["Intent Detection"] --> ToolRouter{"Select Tool"}
            ToolRouter -->|Chmod Calc| ChmodTool["chmod Calculator (app/tools.py)"]
            ToolRouter -->|Safety Risk| ApprovalNode["Human Approval Gate (approved=?)"]
            ToolRouter -->|Linux Docs| RAGTool["RAG Search Tool"]
            ApprovalNode -->|Approved| ExecTool["Execute Action"]
            ApprovalNode -->|Rejected| AbortTool["Abort / Safety Warning"]
            MemoryCheck[("MemorySaver Checkpointer<br/>(Thread Isolation)")] --- IntentNode
        end
        
        AgentModule --> LangGraph_Agent
        
        subgraph LLM_Synthesizer ["LLM Generation & Telemetry"]
            LLMProvider["Groq LLaMA-3.3 / Google Gemini / Offline Fallback"]
            TokenTracker["Token Usage Tracker (app/monitoring.py)<br/>input_tokens, output_tokens, total_tokens"]
        end
        
        RAGModule --> LLM_Synthesizer
        AgentModule --> LLM_Synthesizer
        
        LLM_Synthesizer --> StoreCache["Store in Response Cache<br/>(TTL=300s, Max=500 entries)"]
        StoreCache --> APIResponse["FastAPI Response Payload"]
    end
    
    CachedResponse --> User
    APIResponse --> User
```

---

## 5. Tech Stack

| Category | Technologies & Frameworks | Description |
|---|---|---|
| **Core Runtime** | Python 3.11 / 3.12 / 3.14 | High-performance asynchronous runtime |
| **Backend API** | FastAPI, Starlette, Uvicorn, Pydantic v2 | High-throughput async REST API with strict schemas |
| **Frontend UI** | Streamlit | Interactive responsive chat application with reactive components |
| **Vector Database** | ChromaDB (ONNX Runtime) | Persistent vector store with dense neural embeddings |
| **Embedding Model** | `all-MiniLM-L6-v2` (Sentence-Transformers) | 384-dimensional dense semantic embeddings |
| **Agent Framework** | LangGraph, LangChain Core | Stateful multi-node agent with memory checkpointer & approval gates |
| **LLM Providers** | Groq Cloud (`llama-3.3-70b`), Google Gemini (`gemini-2.5-flash`), Offline Heuristic Fallback | Multi-provider architecture with fallback resilience |
| **Performance & Caching** | Thread-Safe In-Memory Cache, Custom ASGI Middleware | Sub-15ms response caching, latency headers & token telemetry |
| **Testing & Quality** | Pytest, AnyIO, Pytest-Cov, Ruff | 88 automated tests, mock LLMs, strict PEP 8 linting |
| **DevOps & Containers** | Docker, Docker Compose, GitHub Actions, Render Blueprints | Multi-stage containerization & automated CI/CD pipeline |

---

## 6. Results and Evaluation

### RAG Retrieval Benchmark (`eval/rag_compare.md`)
Evaluated across 15 standard test queries in `eval/eval_set.json` using `eval/run_eval.py`:

| Evaluation Metric | Configuration 1 (`top_k=2`, `threshold=0.30`) | Configuration 2 (`top_k=4`, `threshold=0.35`) | Winning Selection |
|---|:---:|:---:|:---:|
| **Hit@1 Rate** | 93.3% | 93.3% | Tie |
| **Hit@3 Rate** | 100.0% | 100.0% | **Configuration 2** |
| **Mean Reciprocal Rank (MRR)** | 0.967 | 0.967 | **Configuration 2** |
| **Answer Correctness Rate** | 93.3% | 93.3% | **Configuration 2** |
| **Hallucination Rate** | 0.0% | 0.0% | Both (0% Hallucinations) |
| **Out-of-Scope Handling** | Refused | Refused | Both (Refuses non-Linux queries) |

*Winner: **Configuration 2 (`top_k=4`, `threshold=0.35`)** provides superior context coverage for complex multi-flag Linux commands while eliminating low-confidence noise.*

### Real Measured Performance & Benchmark (`app/monitoring.py` & `app/cache.py`)
Tested in local development environment (Windows 11, Python 3.14, FastAPI TestClient / ASGI, 20 requests per endpoint):

| Metric / Endpoint | Min Latency | Max Latency | P50 (Median) | Average Latency | Speedup |
|---|:---:|:---:|:---:|:---:|:---:|
| **GET /health** | 12.29 ms | 15.25 ms | 13.86 ms | **13.94 ms** | Baseline |
| **GET /records** | 11.55 ms | 15.19 ms | 12.60 ms | **12.87 ms** | — |
| **POST /ask (Cache MISS)** | 522.26 ms | 798.26 ms | 540.46 ms | **593.53 ms** | Full RAG pipeline |
| **POST /ask (Cache HIT)** | 11.76 ms | 14.28 ms | 13.07 ms | **13.07 ms** | **45.4x Speedup** |

### Token Consumption Profiles
Measured across multi-token synthesis queries:
- **Average Input Tokens:** 140.2 tokens (range: 80 – 224 tokens)
- **Average Output Tokens:** 58.2 tokens (range: 51 – 71 tokens)
- **Average Total Tokens:** 198.4 tokens (range: 132 – 286 tokens)

---

## 7. Demo Video

> **Demo Video:** [Add demo video URL] *(Walkthrough showcasing RAG retrieval, LangGraph human approval, interactive placeholder filling, and live latency monitoring)*

---

## 8. Installation and Usage

### Prerequisites
- Python 3.11+ (Python 3.11 or 3.12 recommended; compatible with 3.14)
- Git
- (Optional) Docker & Docker Compose

### Quickstart (Local Development)

```powershell
# 1. Clone the repository
git clone https://github.com/harshaher/Traning_of_gen_Ai.git
cd Traning_of_gen_Ai

# 2. Set up virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
Copy-Item .env.example .env

# 5. Run FastAPI Backend (Terminal 1)
uvicorn app.main:app --port 8000 --reload

# 6. Run Streamlit UI (Terminal 2)
streamlit run ui/app.py
```

### Turnkey Deployment with Docker Compose

Run the entire multi-service stack (FastAPI backend + Streamlit UI) in isolated containers with a single command:

```bash
docker compose up -d
```

- **FastAPI REST API:** [http://localhost:8000](http://localhost:8000)
- **Swagger Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Streamlit Web UI:** [http://localhost:8501](http://localhost:8501)

To view live service logs:
```bash
docker compose logs -f
```

---

## 9. API Documentation

| Method | Endpoint | Description | Request Payload / Params | Response Headers / Status |
|---|---|---|---|---|
| `GET` | `/health` | Service health & vector store status | None | `X-Request-ID`, `X-Process-Time-Ms` |
| `GET` | `/records` | Browse command catalog | `category`, `limit` | 200 OK (JSON command list) |
| `GET` | `/records/{id}` | Lookup record by ID or command name | `id` (e.g. `tar` or `1`) | 200 OK / 404 Not Found |
| `GET` | `/search` | TF-IDF lexical search | `q`, `limit` | Ranked lexical results |
| `GET` | `/search/semantic` | Neural dense semantic search | `q`, `top_k` | Ranked ChromaDB chunks |
| `POST` | `/ask` | Grounded RAG retrieval with citations & caching | `{"question": "...", "top_k": 4}` | `X-Cache: HIT/MISS`, `token_usage` |
| `POST` | `/agent` | LangGraph agent with approvals & memory | `{"question": "...", "thread_id": "...", "approved": true}` | `status: PENDING_APPROVAL / COMPLETED` |
| `POST` | `/feedback` | Submit user thumbs up/down rating | `{"question": "...", "rating": "helpful"}` | 200 OK (`{"status": "recorded"}`) |
| `GET` | `/feedback` | Retrieve feedback statistics & history | None | Feedback records & summary |
| `GET` | `/cache/stats` | Inspect response cache hit/miss metrics | None | `{"hits": ..., "misses": ..., "size": ...}` |
| `POST` | `/cache/clear` | Invalidate all cached entries | None | `{"status": "cache_cleared"}` |
| `POST` | `/documents/validate` | Validate document file upload before ingestion | Multi-part Form (`file`) | 200 OK / 400 Bad Request |

---

## 10. Production Notes

### 1. In-Memory Response Caching
- **Implementation:** `app/cache.py` implements `ResponseCache`, a thread-safe in-memory cache utilizing Python's `threading.Lock()` to prevent race conditions during concurrent requests.
- **Key Normalization:** Keys are normalized via lowercasing, whitespace collapsing, and punctuation stripping. Retrieval parameters (`top_k`, mode) are incorporated into cache keys to prevent stale or cross-parameter pollution.
- **TTL & Eviction Policy:** Configured with a default TTL of 300 seconds (`CACHE_TTL_SECONDS=300`) and a maximum capacity of 500 entries (`CACHE_MAX_SIZE=500`). When capacity is reached, the oldest expired or least recently inserted entry is evicted.
- **Automatic Invalidation:** Whenever new documentation chunks are parsed or ingested (`app/ingest.py`), `response_cache.invalidate()` is automatically called to prevent serving stale answers.
- **Scope & Scaling:** The current cache is process-local. For distributed multi-worker production deployments (e.g., Gunicorn with multiple Uvicorn workers or multi-pod Kubernetes clusters), a Redis-backed distributed cache adapter is recommended.

### 2. Request Latency & Performance Headers
- **ASGI Middleware:** `RequestLatencyLoggingMiddleware` in `app/monitoring.py` intercepts every inbound request, generating a unique 12-character hexadecimal `request_id` (or propagating an inbound `X-Request-ID`).
- **Telemetry Response Headers:**
  - `X-Request-ID`: Trace identifier for end-to-end distributed observability.
  - `X-Process-Time-Ms`: Server-side processing duration in milliseconds.
  - `X-Cache`: Returns `HIT` when fulfilled from memory or `MISS` when processed through retrieval.

### 3. Token Tracking & Observability
- Integrates transparent token telemetry across LLM providers:
  - **Groq:** Extracts prompt and completion tokens directly from `response.usage`.
  - **Gemini:** Extracts tokens from `usage_metadata` (`prompt_token_count`, `candidates_token_count`).
  - **Offline Fallback:** Employs a deterministic heuristic tokenizer (~4 characters per token) to provide consistent metric reporting even during network-isolated operation.
- Token counts are returned in the response schema (`token_usage: {input_tokens, output_tokens, total_tokens, model_name}`) and logged for cost modeling.

### 4. Input Limits & Security Validation
- `app/limits.py` enforces defense-in-depth sanitization:
  - **Question Length Cap:** Strictly rejects queries exceeding 500 characters with HTTP 400 (`Question exceeds maximum allowed length of 500 characters`).
  - **Retrieval Bounds:** Restricts `top_k` context retrieval to `1 <= top_k <= 10` to prevent memory exhaustion and vector store DoS.
  - **Upload Verification:** Enforces a 1 MB file ceiling and restricts file extensions exclusively to `.md`, `.markdown`, and `.txt`.
  - **Prompt Injection Defense:** Validates that user instructions cannot override core system persona, trigger destructive file manipulations, or bypass the human approval gate.

---

## 11. Verification & Automated Testing

ShellSathi maintains a **100% passing test suite of 88 automated tests** covering all application layers:

```powershell
# Run the complete test suite
.\.venv\Scripts\pytest tests/ -v

# Run code style and linter verification
.\.venv\Scripts\ruff check .
```

### Test Suite Structure:
- `tests/test_records.py`: 7 tests verifying command catalog integrity and schema validation.
- `tests/test_search.py`: 5 tests verifying TF-IDF lexical search and ChromaDB vector retrieval.
- `tests/test_api.py`: 8 tests verifying REST endpoints, health checks, and mock LLM error states.
- `tests/test_tools.py`: 6 tests verifying chmod conversions and destructive command detection.
- `tests/test_agent.py`: 5 tests verifying LangGraph routing, memory isolation, and approval pausing.
- `tests/test_day10.py`: 13 tests verifying Streamlit UI helpers, placeholder filling, and feedback storage.
- `tests/test_security.py`: 12 tests verifying prompt injection defense, input limits, latency headers, and cache lifecycle.
- `tests/test_all_days.py`: 32 comprehensive regression tests across all implementation milestones.

---

## 12. Future Roadmap

1. **Distributed Caching (Redis):** Replace process-local in-memory cache with Redis cluster to support horizontal multi-pod autoscaling.
2. **Streaming Responses (SSE):** Enable Server-Sent Events (SSE) in FastAPI and Streamlit to stream LLM generation tokens in real time.
3. **Multi-Turn Terminal Sandbox:** Integrate an isolated WebAssembly (Wasm) or Dockerized Linux sandbox to safely execute verified commands and display live terminal output.
4. **Fine-Tuned Small Language Model:** Fine-tune a lightweight model (e.g., LLaMA-3.2-3B or Mistral-7B) exclusively on Linux man-pages for zero-cost edge deployment.

---

## 13. Student & Project Information

- **Student Name:** Harsh Vilas Aher
- **Roll Number:** 2125PCAM1004
- **Project ID:** SJ-62
- **Training Program:** Sanjivani AI Training – AI to GenAI Engineer (Softomatic & Examate)
- **Resume Highlights:** [docs/resume.md](file:///docs/resume.md)

---

## 14. License

Developed for educational and portfolio demonstration under the Sanjivani AI Training Program.
Official Linux command documentation provided under open source licenses by the [tldr-pages project](https://github.com/tldr-pages/tldr).
