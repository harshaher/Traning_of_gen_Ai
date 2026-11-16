# ShellSathi — Intelligent Linux Command Assistant

ShellSathi is a beginner-friendly, production-ready Linux command assistant developed for students, system administrators, and developers. It unifies command reference management, TF-IDF lexical search, dense neural embeddings in persistent ChromaDB, Retrieval-Augmented Generation (RAG) with source verification, and a stateful LangGraph autonomous agent with safety approvals and chmod permission calculations.

---

## 1. Student & Project Information

- **Student Name:** Harsh Vilas Aher
- **Roll Number / Student ID:** 2125PCAM1004
- **Project ID:** SJ-62
- **Training Program:** Sanjivani AI Training – AI to GenAI Engineer (Softomatic & Examate)
- **Project Name:** ShellSathi
- **Official Data Source:** [tldr-pages](https://github.com/tldr-pages/tldr)

---

## 2. Project Architecture & Evolution (Day 1 to Day 9)

```text
                  +----------------------------------------------+
                  |              User Request / Query            |
                  +----------------------------------------------+
                                         |
                                         v
                  +----------------------------------------------+
                  |         FastAPI REST API / Swagger UI        |
                  +----------------------------------------------+
                                         |
         +-------------------------------+-------------------------------+
         |                               |                               |
         v                               v                               v
+------------------+           +------------------+            +-------------------+
|  TF-IDF Search   |           |  RAG Subsystem   |            |  LangGraph Agent  |
| (Lexical Search) |           | (Dense Semantic) |            |  (State Machine)  |
+------------------+           +------------------+            +-------------------+
         |                               |                               |
         v                               v                               v
+------------------+           +------------------+            +-------------------+
|   records.json   |           | Persistent Chroma|            |  Safety Check &   |
|   (20 Commands)  |           | (all-MiniLM-L6)  |            |  chmod Calculator |
+------------------+           +------------------+            +-------------------+
```

- **Day 1 & 2:** Interactive CLI menus, 20 Linux command catalog, record search, category aggregation, and safety warnings.
- **Day 3:** Ingestion pipeline downloading markdown pages from official TLDR repositories and parsing into structured dataclasses.
- **Day 4:** TF-IDF vectorization and cosine similarity smart search; FastAPI REST API.
- **Day 5:** LLM architecture documentation, tokenization workflows, and strict refusal of out-of-scope non-Linux queries (Q6).
- **Day 6:** Multi-provider LLM integration (Groq & Gemini) enforcing strict JSON schema (`answer`, `confidence`, `follow_up`).
- **Day 7:** Dense neural vector embeddings (384 dimensions) using ONNX `all-MiniLM-L6-v2` in a persistent Chroma database (`/search/semantic`).
- **Day 8:** Complete RAG pipeline (`/ask`) with document chunk context synthesis, verified source citations, and honest refusal for unsupported domains.
- **Day 9:** LangGraph stateful autonomous agent (`/agent`), human-in-the-loop confirmation for destructive operations, and a comprehensive chmod permission calculator.

---

## 3. Project Directory Structure

```text
gen_Ai/
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example
│
├── app/
│   ├── __init__.py          # Application package marker
│   ├── main.py              # Unified FastAPI application (all endpoints)
│   ├── models.py            # Dataclasses & Pydantic request/response schemas
│   ├── records.py           # 20 Linux commands management & queries
│   ├── ingest.py            # TLDR page parser & dataset generator
│   ├── fetch.py             # Official TLDR markdown page fetcher
│   ├── smart_search.py      # TF-IDF cosine similarity search engine
│   ├── llm.py               # Groq & Gemini provider wrapper with JSON formatting
│   ├── chunking.py          # Document chunker preserving page, title, source
│   ├── embed.py             # 384-dim neural embeddings & cosine similarity
│   ├── vectorstore.py       # Persistent Chroma vector store indexer & query engine
│   ├── rag.py               # RAG retrieval, synthesis, citations & honest Q6 refusal
│   ├── tools.py             # chmod calculator & destructive command risk checker
│   ├── agent_loop.py        # Hand-written multi-tool agent loop
│   └── graph.py             # LangGraph stateful agent workflow with approval node
│
├── data/
│   ├── raw/                 # Downloaded raw markdown files (ls, grep, tar, chmod)
│   ├── records.json         # Master dataset of 44 records across 20 Linux commands
│   └── chroma_db/           # Persistent ChromaDB vector collection storage
│
├── docs/
│   └── how_llms_work.md     # LLM fundamentals, tokenization, architecture & Q6 guide
│
├── prompts/
│   ├── system_prompt.txt    # ShellSathi core persona & JSON output instructions
│   ├── task_prompt_1.txt    # Beginner explanation task prompt
│   └── task_prompt_2.txt    # Intermediate system admin task prompt
│
├── eval/
│   ├── questions.json       # 10 core benchmark questions
│   ├── prompt_compare.md    # Side-by-side prompt comparison across benchmark queries
│   ├── search_results.md    # Semantic search retrieval scores and top hits
│   ├── eval_set.json        # 15 RAG evaluation queries (in-scope + adversarial)
│   ├── run_eval.py          # Empirical RAG configuration benchmark runner
│   └── rag_compare.md       # Benchmark results comparing Config 1 vs Config 2
│
├── analysis/
│   └── explore.py           # Pandas dataset exploration and statistics
│
└── tests/
    └── test_all_days.py     # 18 comprehensive automated unit & integration tests
```

---

## 4. Setup & Installation

### Prerequisites
- Python 3.12+ (tested on Python 3.14 on Windows)
- Git

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/harshaher/Traning_of_gen_Ai.git
   cd Traning_of_gen_Ai
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   # Windows PowerShell:
   .\.venv\Scripts\Activate.ps1
   # Linux / macOS:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   Add your API keys in `.env` (optional; offline fallbacks are built-in):
   ```env
   LLM_PROVIDER=groq
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_MODEL=llama-3.3-70b-versatile
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-2.5-flash
   ```

---

## 5. API Endpoints (FastAPI)

Run the application using Uvicorn:
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive Swagger UI documentation is available at: **`http://127.0.0.1:8000/docs`**

| Method | Endpoint | Description | Input / Parameters | Expected Response |
|---|---|---|---|---|
| `GET` | `/` | Root service status and inventory | None | JSON summary of all features |
| `GET` | `/health` | Healthcheck and vector store count | None | `{"status": "ok", "indexed_chunks": 24}` |
| `GET` | `/records` | Browse command catalog | `limit`, `command` | List of records with descriptions |
| `GET` | `/records/{id}` | Lookup record by ID or command name | `id` (e.g. `1` or `grep`) | Single command record |
| `GET` | `/search` | TF-IDF lexical search | `q` (e.g. `tar`), `limit` | Ranked matches with similarity scores |
| `POST` | `/questions` | Natural language question search | `{"question": "How to extract tar?"}` | Recommended commands and list |
| `POST` | `/chat` | AI chat with structured JSON | `{"question": "How to list hidden files?"}` | `{"answer": ..., "confidence": 0.95, "follow_up": ...}` |
| `GET` | `/search/semantic` | Neural dense semantic search | `q` (e.g. `list files long format`) | Semantic search hits from ChromaDB |
| `POST` | `/ask` | Complete RAG retrieval with citations | `{"question": "How to search in files?"}` | Answer synthesized from docs + `sources` |
| `POST` | `/agent` | LangGraph autonomous agent | `{"question": "...", "approved": false}` | Intent, tool output, answer, approval flag |

---

## 6. RAG Evaluation & Winning Configuration

Evaluation was executed across 15 test queries from `eval/eval_set.json` using `eval/run_eval.py`:

| Evaluation Metric | Configuration 1 (top_k=2, thresh=0.30) | Configuration 2 (top_k=4, thresh=0.35) | Winning Selection |
|---|:---:|:---:|:---:|
| **Hit@1 Rate** | 93.3% | 93.3% | Tie |
| **Hit@3 Rate** | 100.0% | 100.0% | **Configuration 2** |
| **Mean Reciprocal Rank (MRR)** | 0.967 | 0.967 | **Configuration 2** |
| **Answer Correctness Rate** | 93.3% | 93.3% | **Configuration 2** |

### Winner: Configuration 2 (`top_k=4`, `threshold=0.35`)
- Provides richer context for multi-flag queries.
- Discards low-similarity noise with the higher `0.35` threshold.
- Strictly adheres to domain boundaries: Question 6 (*"Why is our company VPN slow from the Hinjewadi office today?"*) correctly outputs an honest *"I don't know"* with zero hallucinations.

---

## 7. LangGraph Agent & Chmod Calculator Tool

The Day 9 Agent uses a stateful LangGraph state machine (`app/graph.py`):

```text
                  +-----------------------+
                  |     classify_node     |
                  +-----------------------+
                              |
            +-----------------+-----------------+
            |                 |                 |
     (Destructive)         (chmod)            (RAG)
            v                 v                 v
   +-----------------+  +------------+  +---------------+
   |  approval_node  |  | chmod_node |  |   rag_node    |
   +-----------------+  +------------+  +---------------+
            |                 |                 |
            +-----------------+-----------------+
                              |
                              v
                           [ END ]
```

### chmod Calculator Features (`app/tools.py`)
- **Octal to Symbolic:** `chmod 755` -> `rwxr-xr-x`
- **Symbolic to Octal:** `chmod rwxr-xr-x` -> `755`
- **Entity Permission Breakdown:** Detailed breakdown for User (Owner), Group, and Others.
- **Safety Interceptor:** Queries containing destructive patterns (`rm -rf`, `mkfs`, `dd`, `kill -9`, `chmod 777`) require explicit human confirmation (`approved=True`) before proceeding.

---

## 8. Verification & Running Tests

Execute the full automated test suite verifying all Day 1 to Day 9 features:

```bash
pytest tests/test_all_days.py -v
```

All 18 tests pass with 100% success rate:
- `test_day2_records_count_and_content`: PASSED
- `test_day2_record_functions`: PASSED
- `test_day3_dataclass_models`: PASSED
- `test_day4_smart_search_tfidf`: PASSED
- `test_day4_fastapi_base_endpoints`: PASSED
- `test_day5_out_of_scope_boundary`: PASSED
- `test_day6_chat_endpoint_schema`: PASSED
- `test_day7_semantic_search`: PASSED
- `test_day8_rag_ask_in_scope`: PASSED
- `test_day8_rag_ask_out_of_scope_q6`: PASSED
- `test_day9_chmod_calculator_octal`: PASSED
- `test_day9_chmod_calculator_symbolic`: PASSED
- `test_day9_chmod_calculator_invalid`: PASSED
- `test_day9_agent_loop_tool_routing`: PASSED
- `test_day9_langgraph_workflow_safe`: PASSED
- `test_day9_langgraph_workflow_destructive_approval`: PASSED
- `test_day9_agent_endpoint`: PASSED
- `test_day9_agent_endpoint_destructive`: PASSED

---

## 9. License

Developed for educational purposes under the Sanjivani AI Training Program.
Official Linux command documentation provided under open source licenses by [tldr-pages](https://github.com/tldr-pages/tldr).
