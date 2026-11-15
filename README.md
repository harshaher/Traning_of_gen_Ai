# ShellSathi - Your Smart Linux Command Assistant

ShellSathi is a beginner-friendly Linux command assistant designed to help students, beginners, and developers understand, search, and master Linux commands through intuitive command-line menus, intelligent TF-IDF semantic search, and Large Language Model (LLM) integration.

---

## Student Details
- **Name:** Harsh Vilas Aher
- **Student ID:** 2125PCAM1004
- **College:** Sanjivani University
- **Training Program:** Sanjivani AI Training – AI to GenAI Engineer
- **Project Name:** ShellSathi
- **Repository:** `sanjivani-sj-62-shellsathi`

---

## Project Card

- **Product:** ShellSathi — Intelligent Linux Command Assistant.
- **Target User:** Students, beginners, and developers learning Linux terminal commands.
- **Problem Statement:** Beginners often struggle to memorize Linux command syntax, understand flags/options, and troubleshoot terminal errors.
- **Solution:** ShellSathi provides structured command references, semantic keyword search, practical runnable examples, and AI-powered conversational assistance.
- **Data Source:** Official Linux documentation and [tldr-pages](https://github.com/tldr-pages/tldr).

---

## Technology Stack
- **Programming Language:** Python 3.12+
- **Web Framework:** FastAPI, Starlette, Uvicorn
- **Data Science & ML:** Pandas, Scikit-learn (TF-IDF Vectorizer, Cosine Similarity)
- **Generative AI & LLMs:** Groq API (`llama-3.3-70b-versatile`), Google Gemini API (`gemini-2.5-flash`)
- **Data Formats:** JSON, Markdown
- **Version Control:** Git, GitHub

---

## Project Organization

The repository is structured into distinct, modular training day directories:

```text
gen_Ai/
├── Day1/               # Day 1: Project Introduction and Interactive CLI Menu
│   ├── day01_intro.py
│   ├── day01_menu.py
│   └── README.md
├── Day2/               # Day 2: 20 Core Linux Command Records & CLI
│   ├── app/
│   │   ├── cli.py
│   │   └── records.py
│   ├── data/
│   │   └── sample_records.py
│   ├── requirements.txt
│   └── README.md
├── Day3/               # Day 3: Data Ingestion from Official TLDR Pages
│   ├── app/
│   │   ├── fetch.py
│   │   ├── ingest.py
│   │   └── models.py
│   ├── data/
│   │   ├── raw/
│   │   └── records.json
│   ├── requirements.txt
│   └── README.md
├── Day4/               # Day 4: FastAPI REST API & Smart Search
│   ├── analysis/
│   │   └── explore.py
│   ├── app/
│   │   ├── main.py
│   │   ├── smart_search.py
│   │   └── records.py
│   ├── data/
│   │   └── records.json
│   ├── requirements.txt
│   └── README.md
├── Day5/               # Day 5: LLM Fundamentals & Benchmark Questions
│   ├── docs/
│   │   └── how_llms_work.md
│   └── README.md
├── Day6/               # Day 6: LLM Integration (Groq & Gemini) & Prompt Engineering
│   ├── app/
│   │   ├── llm.py
│   │   ├── main.py
│   │   └── smart_search.py
│   ├── data/
│   │   └── records.json
│   ├── eval/
│   │   ├── prompt_compare.md
│   │   └── run_eval.py
│   ├── prompts/
│   │   ├── system_prompt.txt
│   │   ├── task_prompt_1.txt
│   │   └── task_prompt_2.txt
│   ├── .env.example
│   ├── requirements.txt
│   └── README.md
├── Day7/               # Day 7: Reserved for subsequent module (kept isolated)
├── .env.example        # Environment variable template
├── .gitignore          # Git exclusion rules
├── requirements.txt    # Project dependencies
└── README.md           # Master project documentation
```

---

## Day-by-Day Summary

### Day 1: Project Introduction & CLI Menu
- Explores foundational variables, string formatting (f-strings), and user input.
- Interactive terminal menu with command rule checking.
- Run: `python Day1/day01_menu.py`

### Day 2: Linux Command Records & CLI
- Comprehensive dataset of 20 core Linux commands (`tar`, `ls`, `cd`, `cp`, `mv`, `rm`, `chmod`, `chown`, `grep`, `find`, `df`, `du`, `ps`, `kill`, `top`, `systemctl`, `journalctl`, `ssh`, `scp`, `curl`).
- Operations: `load_records()`, `search()`, `count_by()`, `get_by_id()`.
- Interactive CLI with categorized command search.
- Run: `python -m app.cli` (from `Day2/`)

### Day 3: TLDR Data Ingestion
- Automated data fetcher (`app/fetch.py`) downloading raw markdown from official `tldr-pages`.
- Data cleaning and parsing pipeline (`app/ingest.py`) creating structured `Record` dataclass objects.
- Error handling with HTTP timeouts and row-skipping for corrupted data.
- Run: `python -m app.fetch` followed by `python -m app.ingest` (from `Day3/`)

### Day 4: FastAPI & Smart Search
- High-performance REST API with Swagger UI at `/docs`.
- TF-IDF and Cosine Similarity search engine for ranking command relevance.
- Exploratory data analysis with Pandas (`analysis/explore.py`).
- Endpoints: `GET /health`, `GET /records?limit=`, `GET /records/{id}`, `GET /search?q=`, `POST /questions`.
- Tag: `week-1`
- Run: `python -m uvicorn app.main:app --reload` (from `Day4/`)

### Day 5: LLM Fundamentals & Checkpoint 1
- Detailed technical explanation of Large Language Model mechanics (Tokenization, Prediction, Generation).
- ASCII workflow architecture diagram.
- 10 real ShellSathi user questions with benchmark expected outcomes, including honest "I don't know" handling for out-of-scope question Q6 (weather).
- Tag: `checkpoint-1`

### Day 6: LLM Integration & Prompt Engineering
- Multi-provider LLM support: Groq (`llama-3.3-70b-versatile`) and Google Gemini (`gemini-2.5-flash`).
- Production system prompt and specialized task prompts enforcing strict JSON output:
  ```json
  {
    "answer": "...",
    "confidence": 0.0,
    "follow_up": "..."
  }
  ```
- New endpoint: `POST /chat`.
- Evaluation framework (`eval/prompt_compare.md` and `eval/run_eval.py`).
- Run: `python -m uvicorn app.main:app --reload` (from `Day6/`)

---

## Security & Best Practices
- Secret keys (`GROQ_API_KEY`, `GEMINI_API_KEY`) are loaded from `.env` via `python-dotenv`.
- `.env` files are strictly excluded via `.gitignore` and never committed to Git.
- Sample configuration is documented safely in `.env.example`.
