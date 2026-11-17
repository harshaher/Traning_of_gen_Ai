# ShellSathi — Intelligent Linux Command Assistant

ShellSathi is a beginner-friendly, production-ready Linux command assistant developed for students, system administrators, and developers. It unifies command reference management, TF-IDF lexical search, dense neural embeddings in persistent ChromaDB, Retrieval-Augmented Generation (RAG) with source verification, and a stateful LangGraph autonomous agent with conversation memory, human-in-the-loop approvals, and chmod permission calculations.

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
- **Day 9:** LangGraph stateful autonomous agent (`/agent`), conversation memory (`MemorySaver`), human approval step, and bi-directional chmod permission calculator.

---

## 3. Project Directory Structure

```text
gen_Ai/
├── README.md                # Comprehensive documentation & Day 9 viva guide
├── requirements.txt         # Production dependencies (FastAPI, ChromaDB, LangGraph, Pytest)
├── .gitignore               # Clean exclusions (.env, .venv, pycache, .pytest_cache)
├── .env.example             # Safe environment variable template with zero secrets
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
│   └── graph.py             # 6-node LangGraph stateful agent workflow with memory & approval
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
    └── test_all_days.py     # 26 comprehensive automated unit & integration tests
```

---

## 4. Setup & Installation (PowerShell)

### Prerequisites
- Python 3.12+ (tested on Python 3.14 on Windows)
- Git

### Installation Commands

```powershell
# 1. Clone repository
git clone https://github.com/harshaher/Traning_of_gen_Ai.git
cd Traning_of_gen_Ai

# 2. Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install required dependencies
pip install -r requirements.txt

# 4. Set up environment variables
Copy-Item .env.example .env
```

---

## 5. API Endpoints (FastAPI)

Start the local server with Uvicorn:
```powershell
.\.venv\Scripts\uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
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
| `POST` | `/agent` | LangGraph autonomous agent with memory & approval | `{"question": "...", "thread_id": "...", "approved": true}` | Intent, tool output, answer, approval flag |

---

## 6. RAG Evaluation Summary (`eval/rag_compare.md`)

Evaluation was executed across 15 test queries from `eval/eval_set.json` using `eval/run_eval.py`:

| Evaluation Metric | Configuration 1 (top_k=2, thresh=0.30) | Configuration 2 (top_k=4, thresh=0.35) | Winning Selection |
|---|:---:|:---:|:---:|
| **Hit@1 Rate** | 93.3% | 93.3% | Tie |
| **Hit@3 Rate** | 100.0% | 100.0% | **Configuration 2** |
| **Mean Reciprocal Rank (MRR)** | 0.967 | 0.967 | **Configuration 2** |
| **Answer Correctness Rate** | 93.3% | 93.3% | **Configuration 2** |

**Winner: Configuration 2 (`top_k=4`, `threshold=0.35`)**
- Provides richer context for multi-flag queries.
- Discards low-similarity noise with the higher `0.35` threshold.
- Handles out-of-scope queries (Q6: VPN slow from Hinjewadi office) with an honest *"I don't know"* and zero hallucinations.

---

## 7. Day 9: Agent, Tools, LangGraph & Viva Guide

### 1. What is an AI Agent?
An **AI Agent** is an autonomous program that receives a user request, perceives the input, plans which action to take, uses external tools (such as search engines, databases, or calculators), and produces an accurate response without requiring human intervention for routine steps.

### 2. What is a Tool?
A **Tool** is a specialized function or API that an agent can call to perform a specific task that the language model or basic code cannot do reliably on its own. In ShellSathi, our tools are:
- `chmod_calculator`: Accurately converts and validates Linux permissions mathematically.
- `rag_search`: Searches verified local Linux documentation chunks in persistent ChromaDB.
- `check_destructive_command`: Evaluates whether a shell command poses data loss risks.

### 3. What is a Hand-Written Agent Loop?
A **Hand-Written Agent Loop** (`app/agent_loop.py`) is a pure Python implementation of agent decision-making using standard loops, conditions, and regex. It inspects user input, decides whether to invoke `chmod_calculator` or `rag_search`, runs the tool, formats the response, and honestly reports when an answer is not found.

### 4. What is LangGraph?
**LangGraph** is a framework for building stateful, multi-actor applications with Large Language Models. It models the application as a **directed graph** where nodes represent units of work (such as intent detection, tool execution, or approval checks) and edges represent transitions or conditional logic between states.

### 5. How does ShellSathi select tools?
ShellSathi selects tools in the `intent_node`:
- If the question contains permission keywords (`chmod`, `octal`, `symbolic`, `permission`) or permission patterns (`[0-7]{3}` or `[rwx\-]{9}`), it routes to `chmod_node`.
- If the user asks a follow-up question referencing an earlier permission in the same thread, it routes to `chmod_node` using conversation memory.
- If the command is a dangerous shell command (`rm -rf`, `mkfs`, `dd`), it flags a safety warning.
- Otherwise, it routes to `rag_node` to query verified Linux documentation.

### 6. How does chmod_calculator work?
`chmod_calculator` in `app/tools.py` converts permissions bi-directionally:
- **Permission values:** Read = 4, Write = 2, Execute = 1.
- **Symbolic to Octal:** Takes 9 characters (e.g. `rwxr-x---`), breaks into 3 triplets (`rwx`=7, `r-x`=5, `---`=0) and returns `750`.
- **Octal to Symbolic:** Takes 3 digits (e.g. `750`), breaks into digits (`7`=`rwx`, `5`=`r-x`, `0`=`---`) and returns `rwxr-x---`.
- **Validation:** Safely rejects invalid octal digits (e.g. `899`), invalid characters (e.g. `rwxr-x--z`), empty strings, or incorrect lengths without crashing.

### 7. What is Conversation Memory?
**Conversation Memory** allows the agent to remember context from earlier messages in a session. In ShellSathi, LangGraph's `MemorySaver` checkpointer stores state per `thread_id`:
- **Turn 1:** User: *"Convert rwxr-x--- into octal"* -> Agent calculates `750` and stores `last_permission = '750'`.
- **Turn 2:** User: *"What does this permission mean?"* -> Agent recalls `750` from memory and explains the owner, group, and others permissions.
- Different `thread_id` values (e.g. `user_1` vs `user_2`) have completely isolated memories.

### 8. Why is an Approval Step Required?
An **Approval Step** (Human-in-the-Loop) is a safety guardrail. Changing file permissions (`chmod`) or executing destructive commands (`rm -rf`) can compromise system security or cause irreversible data loss. Pausing for explicit human confirmation (`approved=true`) ensures that hazardous or sensitive operations are never executed without user intent.

### 9. How to Run `POST /agent`

#### Initial Request (Pauses for Approval)
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/agent" -Method Post -ContentType "application/json" -Body '{"question": "Convert rwxr-x--- into octal", "thread_id": "student_01"}' | ConvertTo-Json
```
Response:
```json
{
  "answer": "Approval required for chmod_approval: Convert 'rwxr-x---' to '750'. Please confirm (approved=true to proceed, or approved=false to cancel).",
  "tool_used": "chmod_calculator",
  "approval_required": true,
  "thread_id": "student_01",
  "status": "PENDING_APPROVAL"
}
```

#### Approval Request (Resumes and Completes)
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/agent" -Method Post -ContentType "application/json" -Body '{"approved": true, "thread_id": "student_01"}' | ConvertTo-Json
```
Response:
```json
{
  "answer": "The octal permission is 750 (Symbolic: rwxr-x---).\n- Owner: read, write, execute\n- Group: read, execute\n- Others: no permissions",
  "tool_used": "chmod_calculator",
  "approval_required": false,
  "thread_id": "student_01",
  "status": "COMPLETED"
}
```

#### Follow-up Query Using Memory
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/agent" -Method Post -ContentType "application/json" -Body '{"question": "What does this permission mean?", "approved": true, "thread_id": "student_01"}' | ConvertTo-Json
```

---

## 8. Verification & Test Suite

Run the full automated test suite verifying all Day 1 to Day 9 features:

```powershell
.\.venv\Scripts\pytest tests\test_all_days.py -v
```

All 26 automated tests pass with a 100% success rate:
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
- `test_day9_chmod_conversions_all_required`: PASSED
- `test_day9_chmod_validation_errors`: PASSED
- `test_day9_agent_loop_rag_selection`: PASSED
- `test_day9_agent_loop_chmod_selection`: PASSED
- `test_day9_agent_loop_octal_explanation`: PASSED
- `test_day9_agent_loop_unknown_question`: PASSED
- `test_day9_agent_loop_empty_query`: PASSED
- `test_day9_langgraph_rag_execution`: PASSED
- `test_day9_langgraph_chmod_approval_and_rejection`: PASSED
- `test_day9_langgraph_chmod_approval_and_success`: PASSED
- `test_day9_langgraph_conversation_memory_followup`: PASSED
- `test_day9_langgraph_thread_isolation`: PASSED
- `test_day9_api_agent_approval_flow`: PASSED
- `test_day9_api_agent_rejection_flow`: PASSED
- `test_day9_api_agent_preapproved`: PASSED
- `test_day9_api_agent_invalid_input`: PASSED

---

## 9. License

Developed for educational purposes under the Sanjivani AI Training Program.
Official Linux command documentation provided under open source licenses by [tldr-pages](https://github.com/tldr-pages/tldr).
