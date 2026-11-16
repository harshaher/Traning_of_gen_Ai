"""
fetch.py - Download official TLDR documentation for ShellSathi
"""

from pathlib import Path
from typing import List, Optional
import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"

BASE_URL = "https://raw.githubusercontent.com/tldr-pages/tldr/main/pages/common"
DEFAULT_COMMANDS = ["tar", "ls", "grep", "chmod"]


def fetch_tldr_page(command: str, output_dir: Optional[Path] = None, timeout: int = 10) -> Optional[str]:
    """Download single TLDR markdown document and save to disk."""
    dest_dir = output_dir or RAW_DIR
    dest_dir.mkdir(parents=True, exist_ok=True)
    target_file = dest_dir / f"{command}.md"

    url = f"{BASE_URL}/{command}.md"
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        content = response.text
        target_file.write_text(content, encoding="utf-8")
        return content
    except requests.RequestException as err:
        # If offline or remote is unreachable, return existing local file if present
        if target_file.exists():
            return target_file.read_text(encoding="utf-8")
        print(f"Warning: Could not fetch {command}.md: {err}")
        return None


def fetch_all(commands: Optional[List[str]] = None) -> List[str]:
    """Download multiple TLDR documentation files."""
    cmds = commands or DEFAULT_COMMANDS
    results = []
    for cmd in cmds:
        content = fetch_tldr_page(cmd)
        if content:
            results.append(cmd)
    return results


if __name__ == "__main__":
    fetched = fetch_all()
    print(f"Fetched {len(fetched)} documents: {fetched}")
