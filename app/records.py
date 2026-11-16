"""
records.py - Linux command record management and queries for ShellSathi
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "records.json"

CATEGORIES = {
    "tar": "Archive & Compression",
    "ls": "File Management",
    "cd": "Navigation",
    "cp": "File Management",
    "mv": "File Management",
    "rm": "File Management (Destructive)",
    "chmod": "Permissions",
    "chown": "Permissions",
    "grep": "Search & Pattern",
    "find": "Search & Pattern",
    "df": "System & Disk",
    "du": "System & Disk",
    "ps": "Process Management",
    "kill": "Process Management",
    "top": "Process Monitoring",
    "systemctl": "Service Management",
    "journalctl": "Log Management",
    "ssh": "Network & Remote",
    "scp": "Network & Remote",
    "curl": "Network & Web",
}

DESTRUCTIVE_COMMANDS = {"rm", "kill", "chmod"}


def load_records(file_path: Optional[Path | str] = None) -> List[Dict[str, Any]]:
    """Load command records from JSON file."""
    path = Path(file_path) if file_path else DATA_FILE
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as f:
        records = json.load(f)

    # Attach integer 1-based IDs and categories
    for idx, rec in enumerate(records, start=1):
        rec["id"] = idx
        rec["category"] = CATEGORIES.get(rec.get("command", ""), "General Linux")
        if rec.get("command") in DESTRUCTIVE_COMMANDS:
            rec["safety_warning"] = "Warning: This command can modify, terminate, or delete system data."

    return records


def search(records: List[Dict[str, Any]], keyword: str) -> List[Dict[str, Any]]:
    """Search records by keyword across command, description, and task."""
    if not keyword or not keyword.strip():
        return []

    term = keyword.lower().strip()
    matches = []

    for r in records:
        text = f"{r.get('command', '')} {r.get('description', '')} {r.get('example_task', '')} {r.get('example_command', '')}".lower()
        if term in text:
            matches.append(r)

    return matches


def count_by(records: List[Dict[str, Any]], field: str = "category") -> Dict[str, int]:
    """Count records grouped by category or other field."""
    counts: Dict[str, int] = {}
    for r in records:
        val = r.get(field, "Unknown")
        counts[val] = counts.get(val, 0) + 1
    return counts


def get_by_id(records: List[Dict[str, Any]], record_id: Any) -> Optional[Dict[str, Any]]:
    """Retrieve record by integer ID or command name."""
    if isinstance(record_id, int) or (isinstance(record_id, str) and record_id.isdigit()):
        target_id = int(record_id)
        for r in records:
            if r.get("id") == target_id:
                return r

    # Also allow lookup by command string name
    cmd_name = str(record_id).lower().strip()
    for r in records:
        if r.get("command", "").lower() == cmd_name:
            return r

    return None
