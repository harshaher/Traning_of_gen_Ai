import json

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

try:
    from app.smart_search import load_records, search_records
    from app.llm import generate_answer
except ImportError:
    from Day6.app.smart_search import load_records, search_records
    from Day6.app.llm import generate_answer


app = FastAPI(
    title="ShellSathi API",
    description="Smart Linux Command Search and AI Assistant",
    version="2.0.0"
)


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1)


class ChatResponse(BaseModel):
    answer: str
    confidence: float = Field(ge=0, le=1)
    follow_up: str


@app.get("/health")
def health_check():
    return {
        "status": "success",
        "message": "ShellSathi API is running"
    }


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


@app.get("/records/{record_id}")
def get_record(record_id: int):
    records = load_records()

    if record_id < 1 or record_id > len(records):
        raise HTTPException(status_code=404, detail="Record not found")

    result = records[record_id - 1].copy()
    result["id"] = record_id

    return result


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


@app.post("/questions")
def ask_question(request: QuestionRequest):
    results = search_records(request.question, limit=5)

    return {
        "question": request.question,
        "total_results": len(results),
        "answer": (
            "Here are the relevant Linux commands."
            if results
            else "No matching Linux command found."
        ),
        "results": results
    }


@app.post("/chat", response_model=ChatResponse)
def chat_with_shellsathi(request: ChatRequest):
    try:
        answer_text = generate_answer(request.question)

        # Clean markdown code fences if present in LLM response
        clean_text = answer_text.strip()
        if clean_text.startswith("```"):
            lines = clean_text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            clean_text = "\n".join(lines).strip()

        # Parse the JSON returned by the LLM
        answer_data = json.loads(clean_text)

        # Validate the response structure
        return ChatResponse(**answer_data)

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=502,
            detail="LLM returned invalid JSON."
        )

    except ValueError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error)
        )

    except Exception:
        raise HTTPException(
            status_code=502,
            detail="LLM provider request failed. Check provider configuration."
        )
