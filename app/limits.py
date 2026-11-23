"""
limits.py - Input Limits and Security Validation for ShellSathi (S1)

Enforces:
  - Maximum question character length
  - Maximum retrieval top_k boundary
  - Document upload size limit and allowed file extensions
  - Protection against excessively large or malicious payloads
"""

import os
from typing import Set

from fastapi import HTTPException

MAX_QUESTION_LENGTH: int = int(os.getenv("MAX_QUESTION_LENGTH", "500"))
MIN_TOP_K: int = int(os.getenv("MIN_TOP_K", "1"))
MAX_TOP_K: int = int(os.getenv("MAX_TOP_K", "10"))
MAX_UPLOAD_SIZE_BYTES: int = int(os.getenv("MAX_UPLOAD_SIZE_BYTES", str(1024 * 1024)))
ALLOWED_DOCUMENT_EXTENSIONS: Set[str] = {".md", ".markdown", ".txt"}


def validate_question_length(question: str, max_length: int = MAX_QUESTION_LENGTH) -> str:
    """
    Validate that question text does not exceed the maximum allowed length.
    Raises HTTPException(400) with a clear error message.
    """
    if question is None:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be null.",
        )
    clean = question.strip()
    if not clean:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty or contain only whitespace.",
        )
    if len(question) > max_length:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Question exceeds maximum allowed length of {max_length} characters "
                f"(received {len(question)} characters)."
            ),
        )
    return clean


def validate_retrieval_top_k(top_k: int, min_k: int = MIN_TOP_K, max_k: int = MAX_TOP_K) -> int:
    """
    Validate that top_k retrieval size is within safe bounds [min_k, max_k].
    Raises HTTPException(400) if out of bounds.
    """
    if top_k < min_k or top_k > max_k:
        raise HTTPException(
            status_code=400,
            detail=f"Parameter 'top_k' must be between {min_k} and {max_k} (received {top_k}).",
        )
    return top_k


def validate_upload_file(filename: str, file_size_bytes: int) -> None:
    """
    Validate document upload properties:
      - File extension must be in ALLOWED_DOCUMENT_EXTENSIONS (.md, .markdown, .txt)
      - File size must not exceed MAX_UPLOAD_SIZE_BYTES (1 MB)
    """
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_DOCUMENT_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"File type '{ext}' is not permitted. "
                f"Allowed file types: {sorted(ALLOWED_DOCUMENT_EXTENSIONS)}"
            ),
        )
    if file_size_bytes > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"File size {file_size_bytes} bytes exceeds maximum allowed limit of "
                f"{MAX_UPLOAD_SIZE_BYTES} bytes (1 MB)."
            ),
        )
