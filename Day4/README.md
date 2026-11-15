# ShellSathi - Day 4: FastAPI & Smart Search

Day 4 adds a REST API using FastAPI, intelligent search powered by TF-IDF and Cosine Similarity, and data analysis using Pandas.

## Features
- **FastAPI Backend**: High-performance REST API with automatic Swagger UI documentation.
- **Smart Search**: Ranks Linux commands using TF-IDF vectorization and Cosine Similarity.
- **Data Exploration**: Explores dataset statistics using Pandas.

## Folder Structure
```text
Day4/
├── analysis/
│   └── explore.py        # Pandas analysis printing facts about records
├── app/
│   ├── main.py           # FastAPI application and endpoints
│   ├── smart_search.py   # TF-IDF & Cosine Similarity search engine
│   ├── records.py        # Record helpers
│   └── __init__.py
├── data/
│   ├── records.json      # Ingested command records
│   └── sample_records.py # Sample command records
├── requirements.txt
└── README.md
```

## How to Run

### 1. Run Data Analysis
```bash
python analysis/explore.py
```
This prints key dataset facts:
- Total records
- Unique commands
- Records by platform
- Most common command

### 2. Start the FastAPI Server
From the `Day4` directory:
```bash
python -m uvicorn app.main:app --reload
```
The server will start at `http://127.0.0.1:8000`.

### 3. Open API Documentation
Open your browser and navigate to:
```text
http://127.0.0.1:8000/docs
```
Swagger UI provides interactive testing for all endpoints.

## API Endpoints

| Method | Endpoint | Query / Body | Description |
|---|---|---|---|
| GET | `/health` | None | API health status |
| GET | `/records` | `?limit=10` | Retrieve command records (with limit) |
| GET | `/records/{id}` | Path param `id` | Retrieve specific record by ID (404 if missing) |
| GET | `/search` | `?q=query&limit=10` | TF-IDF ranked search |
| POST | `/questions` | `{"question": "..."}` | Submit natural language question |

## Example Request & Response

### Smart Search:
`GET /search?q=tar archive`
```json
{
  "query": "tar archive",
  "total_results": 8,
  "results": [
    {
      "command": "tar",
      "platform": "linux",
      "description": "Archiving utility...",
      "example_task": "List the contents of a tar file",
      "example_command": "tar tvf path/to/source.tar",
      "id": 23,
      "score": 0.7891
    }
  ]
}
```

### Ask Question:
`POST /questions` with body `{"question": "How to list files?"}`
```json
{
  "question": "How to list files?",
  "total_results": 5,
  "answer": "Here are the relevant Linux commands.",
  "results": [...]
}
```
