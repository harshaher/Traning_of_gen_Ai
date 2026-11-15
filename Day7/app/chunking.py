"""
chunking.py - ShellSathi Document Chunking Module

Splits Linux command reference documents into semantically coherent chunks
while preserving essential metadata:
  - source: Document URL or file source
  - page: Command name / manual page (e.g. ls, grep, tar)
  - title: Specific task / operation title (e.g. "List all files, including hidden files")
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class DocumentChunk:
    """Represents an indexed chunk with search text and traceability metadata."""
    chunk_id: str
    text: str
    source: str
    page: str
    title: str

    @property
    def metadata(self) -> Dict[str, Any]:
        """Return metadata dict suitable for Chroma vector store storage."""
        return {
            "source": self.source,
            "page": self.page,
            "title": self.title,
            "chunk_id": self.chunk_id,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert chunk to standard dictionary."""
        data = asdict(self)
        data["metadata"] = self.metadata
        return data


def clean_command_syntax(cmd_template: str) -> str:
    """
    Clean tldr template placeholders like {{[-a|--all]}} into readable flags like -a.
    """
    cleaned = re.sub(r"\{\{\[?-([a-zA-Z0-9]+)\|[^}]+\]?\}\}", r"-\1", cmd_template)
    cleaned = re.sub(r"\{\{([^\}]+)\}\}", r"\1", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def chunk_markdown_file(file_path: Path | str) -> List[DocumentChunk]:
    """
    Parse a tldr-style markdown document into individual command chunks.
    Preserves:
      - source: The file path or web reference from header
      - page: The command name (# ls -> ls)
      - title: The specific example task description
    """
    path = Path(file_path)
    if not path.exists():
        return []

    content = path.read_text(encoding="utf-8")
    page_name = path.stem
    source_url = f"https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common/{path.name}"
    description_lines: List[str] = []

    # Extract header information
    lines = content.splitlines()
    for line in lines:
        line_s = line.strip()
        if line_s.startswith("# "):
            page_name = line_s.replace("# ", "").strip()
        elif line_s.startswith("> More information:"):
            url_match = re.search(r"<(https?://[^>]+)>", line_s)
            if url_match:
                source_url = url_match.group(1)
        elif line_s.startswith("> "):
            desc_text = line_s.replace("> ", "").strip()
            if not desc_text.startswith("More information"):
                description_lines.append(desc_text)

    command_description = " ".join(description_lines)

    # Regex to find:
    # - Example Title:
    # `example_command`
    pattern = re.compile(
        r"-\s+(?P<title>[^:\n]+):\s*\n+`(?P<command>[^`]+)`",
        re.MULTILINE
    )

    chunks: List[DocumentChunk] = []
    for idx, match in enumerate(pattern.finditer(content)):
        title = match.group("title").strip()
        raw_cmd = match.group("command").strip()
        cmd_readable = clean_command_syntax(raw_cmd)

        chunk_id = f"chunk_{page_name}_{idx + 1}"
        chunk_text = (
            f"Command: {page_name}\n"
            f"Title: {title}\n"
            f"Usage: {cmd_readable}\n"
            f"Template: {raw_cmd}\n"
            f"Description: {command_description}"
        ).strip()

        chunks.append(
            DocumentChunk(
                chunk_id=chunk_id,
                text=chunk_text,
                source=source_url,
                page=page_name,
                title=title,
            )
        )

    return chunks


def chunk_records_file(records_path: Path | str) -> List[DocumentChunk]:
    """
    Chunk ShellSathi records.json, preserving source, page (command), and title (example_task).
    """
    path = Path(records_path)
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as f:
        records = json.load(f)

    chunks: List[DocumentChunk] = []
    for idx, rec in enumerate(records):
        page = rec.get("command", "unknown")
        title = rec.get("example_task", "Command usage")
        raw_cmd = rec.get("example_command", "")
        cmd_readable = clean_command_syntax(raw_cmd)
        description = rec.get("description", "")
        source = rec.get("source_url", f"https://man7.org/linux/man-pages/man1/{page}.1.html")

        chunk_id = f"chunk_{page}_{idx + 1}"
        chunk_text = (
            f"Command: {page}\n"
            f"Title: {title}\n"
            f"Usage: {cmd_readable}\n"
            f"Template: {raw_cmd}\n"
            f"Description: {description}"
        ).strip()

        chunks.append(
            DocumentChunk(
                chunk_id=chunk_id,
                text=chunk_text,
                source=source,
                page=page,
                title=title,
            )
        )

    return chunks


def load_all_chunks(base_dir: Optional[Path | str] = None) -> List[DocumentChunk]:
    """
    Load and chunk all ShellSathi documents.
    Prefers records.json (which contains curated records with source_url),
    or falls back to raw markdown documents in data/raw.
    """
    if base_dir is None:
        base_dir = Path(__file__).resolve().parent.parent

    base_path = Path(base_dir)
    records_file = base_path / "data" / "records.json"
    raw_dir = base_path / "data" / "raw"

    if records_file.exists():
        return chunk_records_file(records_file)
    elif raw_dir.exists():
        all_chunks: List[DocumentChunk] = []
        for md_file in sorted(raw_dir.glob("*.md")):
            all_chunks.extend(chunk_markdown_file(md_file))
        return all_chunks
    else:
        return []


if __name__ == "__main__":
    chunks = load_all_chunks()
    print(f"Loaded {len(chunks)} chunks.")
    if chunks:
        sample = chunks[0]
        print(f"Sample Chunk ID: {sample.chunk_id}")
        print(f"Source: {sample.source}")
        print(f"Page: {sample.page}")
        print(f"Title: {sample.title}")
        print(f"Text Preview:\n{sample.text[:150]}...")
