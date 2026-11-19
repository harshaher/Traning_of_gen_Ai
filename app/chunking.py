"""
chunking.py - Document chunking preserving source, page, and title metadata
"""

import json
import re
from pathlib import Path
from typing import List, Optional

from app.models import DocumentChunk

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_FILE = PROJECT_ROOT / "data" / "records.json"


def clean_template_syntax(template: str) -> str:
    """Clean placeholders such as {{[-a|--all]}} into readable flags like -a."""
    cleaned = re.sub(r"\{\{\[?-([a-zA-Z0-9]+)\|[^}]+\]?\}\}", r"-\1", template)
    cleaned = re.sub(r"\{\{([^\}]+)\}\}", r"\1", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


def chunk_from_records(records_path: Path = DATA_FILE) -> List[DocumentChunk]:
    """Create document chunks from data/records.json."""
    if not records_path.exists():
        return []

    with open(records_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    chunks: List[DocumentChunk] = []
    for idx, rec in enumerate(records, start=1):
        cmd = rec.get("command", "unknown")
        task = rec.get("example_task", "Linux Command Operation")
        example = rec.get("example_command", "")
        desc = rec.get("description", "")
        source = rec.get("source_url", f"https://tldr.sh/linux/{cmd}")

        readable_cmd = clean_template_syntax(example)
        chunk_id = f"chunk_{cmd}_{idx}"

        text = (
            f"Command: {cmd}\n"
            f"Title: {task}\n"
            f"Usage: {readable_cmd}\n"
            f"Template: {example}\n"
            f"Description: {desc}"
        ).strip()

        chunks.append(
            DocumentChunk(
                chunk_id=chunk_id,
                text=text,
                source=source,
                page=cmd,
                title=task,
            )
        )

    return chunks


def load_all_chunks(base_dir: Optional[Path] = None) -> List[DocumentChunk]:
    """Load and chunk all ShellSathi documents."""
    root = base_dir or PROJECT_ROOT
    records_file = root / "data" / "records.json"
    return chunk_from_records(records_file)


if __name__ == "__main__":
    all_chunks = load_all_chunks()
    print(f"Loaded {len(all_chunks)} chunks.")
    if all_chunks:
        print(f"Sample: {all_chunks[0].chunk_id} -> {all_chunks[0].page}: {all_chunks[0].title}")
