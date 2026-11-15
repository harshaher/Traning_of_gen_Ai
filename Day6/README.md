# ShellSathi - Day 6: LLM Integration & Prompt Engineering

Day 6 integrates Large Language Models (Groq and Google Gemini) with the ShellSathi FastAPI backend, enforces strict JSON responses, and establishes a prompt comparison evaluation framework.

## Features
- **Multi-Provider LLM Integration**: Supports Groq (Llama models) and Google Gemini with runtime selection via `LLM_PROVIDER`.
- **System & Task Prompts**:
  - `prompts/system_prompt.txt`: Production system prompt enforcing beginner-friendly tone, Linux safety rules, and strict JSON output.
  - `prompts/task_prompt_1.txt`: Command explanation task template.
  - `prompts/task_prompt_2.txt`: Problem-solving task template.
- **REST Endpoints**:
  - `POST /chat`: Generates structured responses (`answer`, `confidence`, `follow_up`).
  - `GET /health`, `GET /records`, `GET /records/{id}`, `GET /search`, `POST /questions`.
- **Prompt Evaluation Framework**:
  - `eval/prompt_compare.md`: 10-question evaluation benchmark comparing Baseline vs. ShellSathi System Prompt.
  - `eval/run_eval.py`: Automated runner for offline prompt validation and live evaluation.

## Folder Structure
```text
Day6/
├── app/
│   ├── llm.py            # Groq & Gemini provider integration
│   ├── main.py           # FastAPI application with /chat endpoint
│   ├── smart_search.py   # TF-IDF & Cosine Similarity search engine
│   └── __init__.py
├── data/
│   └── records.json      # Command dataset
├── eval/
│   ├── prompt_compare.md # Prompt comparison evaluation table
│   └── run_eval.py       # Evaluation runner script
├── prompts/
│   ├── system_prompt.txt # ShellSathi system prompt
│   ├── task_prompt_1.txt # Command explanation task prompt
│   └── task_prompt_2.txt # Problem solving task prompt
├── .env.example          # Environment variable template
├── .gitignore            # Ignores .env and .venv
├── requirements.txt
└── README.md
```

## Setup & Configuration

1. **Environment Variables**:
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   Configure your preferred provider and API key in `.env`:
   ```env
   LLM_PROVIDER=groq
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_MODEL=llama-3.3-70b-versatile

   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-2.5-flash
   ```
   > **Note:** Never commit the `.env` file to Git.

2. **Run Evaluation Script**:
   ```bash
   python -m eval.run_eval
   ```
   This performs offline prompt and schema validation, or runs live requests if API keys are set.

3. **Start the API Server**:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

4. **Test the `/chat` Endpoint**:
   ```bash
   curl -X POST http://127.0.0.1:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"question": "How do I list files in Linux?"}'
   ```
   Response format:
   ```json
   {
     "answer": "Use the ls command to list directory contents...",
     "confidence": 0.95,
     "follow_up": "Would you like to know how to view hidden files as well?"
   }
   ```
