from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from app.smart_search import load_records, search_records

app = FastAPI(
    title="ShellSathi API",
    description="Smart Linux Command Search API",
    version="1.0.0"
)


# Request model for questions
class QuestionRequest(BaseModel):
    question: str = Field(min_length=1)


# Health Check API
@app.get("/health")
def health_check():
    return {
        "status": "success",
        "message": "ShellSathi API is running"
    }


# Get all records
@app.get("/records")
def get_records(limit: int = Query(default=10, ge=1, le=100)):
    records = load_records()

    results = []

    for index, record in enumerate(records[:limit]):
        item = record.copy()
        item["id"] = index + 1
        results.append(item)

    return {
        "total": len(records),
        "showing": len(results),
        "records": results
    }


# Get record by ID
@app.get("/records/{record_id}")
def get_record(record_id: int):

    records = load_records()

    if record_id < 1 or record_id > len(records):
        raise HTTPException(
            status_code=404,
            detail="Record not found"
        )

    result = records[record_id - 1].copy()
    result["id"] = record_id

    return result


# Smart Search API
@app.get("/search")
def search(
    q: str = Query(min_length=1),
    limit: int = Query(default=10, ge=1, le=100)
):
    results = search_records(q, limit)

    return {
        "query": q,
        "total_results": len(results),
        "results": results
    }


# Ask ShellSathi API
@app.post("/questions")
def ask_question(request: QuestionRequest):

    question = request.question

    results = search_records(question, limit=5)

    return {
        "question": question,
        "total_results": len(results),
        "answer": (
            "Here are the relevant Linux commands."
            if results
            else "No matching Linux command found."
        ),
        "results": results
    }