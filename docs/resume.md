# ShellSathi — Professional Resume Highlights

> **Candidate:** Harsh Vilas Aher | **Project:** ShellSathi (AI-Powered Linux Command Assistant)  
> **Repository:** [https://github.com/harshaher/Traning_of_gen_Ai](https://github.com/harshaher/Traning_of_gen_Ai)  
> **Tech Stack:** Python, FastAPI, Streamlit, ChromaDB, LangGraph, LangChain, Groq/Gemini APIs, Docker, GitHub Actions, Pytest, Ruff

---

### Resume Bullet Points (Selectable for Software Engineer / AI Engineer Roles)

* **Architected and deployed ShellSathi**, an enterprise-grade Linux Command Assistant featuring a hybrid RAG pipeline (TF-IDF keyword + ChromaDB dense vector retrieval) and a LangGraph human-in-the-loop agent that safeguards destructive terminal operations (`rm -rf`, `chmod 777`) with interactive human approval workflows.
* **Engineered production backend infrastructure in FastAPI**, implementing an in-memory TTL response cache that delivered a **45.4x latency reduction** (from 593ms to 13ms), custom ASGI request latency middleware (`X-Request-ID`, `X-Process-Time-Ms`), and real-time token telemetry across Groq, Gemini, and offline heuristic synthesizers.
* **Implemented comprehensive QA and security safeguards**, authoring 88 automated Pytest test suites covering prompt-injection defense, strict input validation limits, and multi-turn state isolation; established continuous integration and automated testing via GitHub Actions and Docker containerization.
