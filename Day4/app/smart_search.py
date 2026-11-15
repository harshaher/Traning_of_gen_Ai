import json
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Project मधील records.json चा path
DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "records.json"


def load_records():
    """Load records from JSON file."""

    if not DATA_FILE.exists():
        return []

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def search_records(query, limit=10):
    """Search records using TF-IDF and Cosine Similarity."""

    records = load_records()

    if not query or not query.strip() or not records:
        return []

    documents = []

    for record in records:
        text = " ".join([
            str(record.get("command", "")),
            str(record.get("platform", "")),
            str(record.get("description", "")),
            str(record.get("example_task", "")),
            str(record.get("example_command", ""))
        ])

        documents.append(text)

    try:
        vectorizer = TfidfVectorizer(stop_words="english")

        record_vectors = vectorizer.fit_transform(documents)
        query_vector = vectorizer.transform([query])

        scores = cosine_similarity(
            query_vector,
            record_vectors
        ).flatten()

    except ValueError:
        return []

    results = []

    for index, score in enumerate(scores):
        if score > 0:
            result = records[index].copy()

            # प्रत्येक record ला stable ID
            result["id"] = index + 1
            result["score"] = round(float(score), 4)

            results.append(result)

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return results[:limit]