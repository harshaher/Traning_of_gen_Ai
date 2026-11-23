"""
ingest.py - Parse raw TLDR Markdown files into structured command records
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List

from app.models import Record

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_FILE = PROJECT_ROOT / "data" / "records.json"


def parse_markdown(file_path: Path) -> List[Record]:
    """Parse single TLDR markdown file into Record dataclass objects."""
    records = []
    if not file_path.exists():
        return records

    content = file_path.read_text(encoding="utf-8")
    command_name = file_path.stem
    source_url = (
        f"https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common/{file_path.name}"
    )

    description_lines = []
    for line in content.splitlines():
        line_s = line.strip()
        if line_s.startswith("> ") and not line_s.startswith("> More information"):
            description_lines.append(line_s[2:].strip())

    description = " ".join(description_lines) or f"Linux {command_name} command."

    pattern = re.compile(r"-\s+([^:\n]+):\s*\n+`([^`]+)`")

    for match in pattern.finditer(content):
        try:
            task = match.group(1).strip()
            cmd_template = match.group(2).strip()

            rec = Record(
                command=command_name,
                platform="Linux",
                description=description,
                example_task=task,
                example_command=cmd_template,
                source_url=source_url,
            )
            records.append(rec)
        except Exception as err:
            print(f"Skipping bad row in {file_path.name}: {err}")
            continue

    return records


def ingest_all(raw_dir: Path = RAW_DIR, output_file: Path = DATA_FILE) -> int:
    """Ingest all raw markdown files and update data/records.json."""
    all_parsed_records: List[Dict[str, Any]] = []

    for md_file in sorted(raw_dir.glob("*.md")):
        recs = parse_markdown(md_file)
        all_parsed_records.extend([r.to_dict() for r in recs])

    existing_records = []
    if output_file.exists():
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                existing_records = json.load(f)
        except Exception:
            existing_records = []

    task_keys = set(r["example_task"].lower() for r in all_parsed_records)
    merged = list(all_parsed_records)

    for r in existing_records:
        if r.get("example_task", "").lower() not in task_keys:
            merged.append(r)
            task_keys.add(r.get("example_task", "").lower())

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=4)

    try:
        from app.cache import response_cache

        response_cache.invalidate()
    except Exception:
        pass

    return len(merged)


if __name__ == "__main__":
    count = ingest_all()
    print(f"Ingested records successfully. Total records: {count}")
