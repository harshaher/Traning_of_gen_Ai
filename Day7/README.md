# ShellSathi - Day 7: Document Chunking, Dense Embeddings & Persistent Chroma Vector Search

**Student:** Harsh Vilas Aher (Student ID: `2125PCAM1004`)  
**Program:** Sanjivani AI Training – AI to GenAI Engineer (`SJ-62`)  
**Product:** ShellSathi (Intelligent Linux Command Assistant)  
**Day 7 Milestone:** Document Chunking, Dense Semantic Embeddings, Persistent Chroma Vector Store, and Semantic Search API.

---

## 1. Overview & Architecture

Day 7 upgrades ShellSathi from keyword/exact matching and raw LLM prompting to a full **Retrieval-Augmented Generation (RAG) vector foundation**:

```
[ Raw Linux Manuals / Records ]
             │
             ▼
     app/chunking.py         (Extracts chunks preserving source, page, title)
             │
             ▼
      app/embed.py           (Computes 384-dimensional dense semantic vectors)
             │
             ▼
    app/vectorstore.py       (Persistent Chroma collection in data/chroma/)
             │
             ▼
       app/main.py           (FastAPI endpoint: GET /search/semantic?q=)
             │
             ▼
    eval/search_results.md   (Evaluation of 10 benchmark ShellSathi questions)
```

---

## 2. Requirements & Deliverables

### S1: Document Chunking & Dense Embeddings
- `app/chunking.py`:
  - Parses Linux command reference documents (`data/raw/*.md` and `data/records.json`).
  - Preserves essential provenance metadata for every chunk:
    - **`source`**: Upstream documentation URL (e.g. `https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common/ls.md`).
    - **`page`**: Target Linux command / manual page (e.g. `ls`, `grep`, `tar`).
    - **`title`**: Specific human-readable operation task (e.g. `List all files, including hidden files`).
    - **`chunk_id`**: Deterministic unique chunk identifier.
- `app/embed.py`:
  - Generates 384-dimensional dense vector embeddings.
  - Implements Chroma's `EmbeddingFunction` protocol for direct vector store integration.
  - Computes cosine similarity with L2 normalization.
- `eval/search_results.md`:
  - Systematic benchmark of all 10 ShellSathi user questions.
  - Records top hits, similarity scores, metadata, and handles out-of-scope question Q6.

### S2: Persistent Chroma Vector Store & Semantic API
- `app/vectorstore.py`:
  - Persistent Chroma vector store stored in `Day7/data/chroma/`.
  - Manages collection `shellsathi_chunks`.
  - Supports automated indexing, idempotent upsert, and fast cosine similarity queries.
- `app/main.py`:
  - Exposes `GET /search/semantic?q=...` returning ranked results with `chunk_id`, `score`, `source`, `page`, `title`, and `text`.
  - Includes `GET /health`, `GET /records`, and interactive Swagger documentation at `/docs`.

---

## 3. Directory Layout

```
Day7/
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules for Day 7
├── README.md                 # Complete documentation
├── requirements.txt          # Python dependencies
├── app/
│   ├── __init__.py           # Package marker
│   ├── chunking.py           # Document chunker preserving metadata
│   ├── embed.py              # Dense vector embedding function
│   ├── main.py               # FastAPI application with /search/semantic
│   └── vectorstore.py        # Persistent Chroma vector store wrapper
├── data/
│   ├── records.json          # Curated Linux command records
│   ├── raw/                  # Raw markdown command manuals (ls, grep, tar)
│   └── chroma/               # Persistent Chroma vector database
└── eval/
    ├── run_eval.py           # Benchmark evaluation runner
    └── search_results.md     # Detailed hits for all 10 benchmark questions
```

---

## 4. Benchmark Questions & Semantic Search Results

All 10 benchmark questions were evaluated against the indexed ShellSathi corpus:

| ID | Benchmark Question | Expected Command | Category | Status |
|---|---|---|---|---|
| **Q1** | How can I list files in Linux? | `ls` | In-Scope | **Matched** (`ls -1`) |
| **Q2** | How can I search for a pattern inside files? | `grep` | In-Scope | **Matched** (`grep pattern`) |
| **Q3** | How can I display hidden files? | `ls -a` | In-Scope | **Matched** (`ls -a`) |
| **Q4** | How can I search for an exact string in a file? | `grep -F` | In-Scope | **Matched** (`grep -F`) |
| **Q5** | How can I list files in long format? | `ls -l` | In-Scope | **Matched** (`ls -l`) |
| **Q6** | What will the weather be tomorrow? | Out of Scope | Out-of-Scope | **Low Score** (Properly rejected) |
| **Q7** | How can I search inside files recursively? | `grep -r` | In-Scope | **Matched** (`grep -r`) |
| **Q8** | How can I create a compressed archive? | `tar -czvf` | In-Scope | **Matched** (`tar -czvf`) |
| **Q9** | How can I extract an archive into a target directory? | `tar -xvf -C` | In-Scope | **Matched** (`tar -xvf -C`) |
| **Q10** | How can I list the contents of a tar archive? | `tar -tvf` | In-Scope | **Matched** (`tar -tvf`) |

Full evaluation details and top-3 hits are documented in [eval/search_results.md](eval/search_results.md).

---

## 5. How to Run and Test

### 1. Install Dependencies
```bash
pip install -r Day7/requirements.txt
```

### 2. Run Semantic Search Evaluation
```bash
python Day7/eval/run_eval.py
```

### 3. Start the FastAPI Server
```bash
uvicorn Day7.app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Query the Semantic Search Endpoint
```bash
curl -X GET "http://localhost:8000/search/semantic?q=How%20can%20I%20display%20hidden%20files%3F"
```

Example JSON Response:
```json
{
  "query": "How can I display hidden files?",
  "total_hits": 5,
  "results": [
    {
      "rank": 1,
      "chunk_id": "chunk_ls_10",
      "score": 0.7072,
      "source": "https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common/ls.md",
      "page": "ls",
      "title": "List all files, including hidden files",
      "text": "Command: ls\nTitle: List all files, including hidden files\nUsage: ls -a..."
    }
  ]
}
```

### 5. Access Interactive Swagger Docs
Open `http://localhost:8000/docs` in your browser.
