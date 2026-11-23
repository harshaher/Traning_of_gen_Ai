"""
placeholder.py - ShellSathi Signature Feature: Dynamic Placeholder Filler

Extracts, validates, and fills Linux command placeholders (e.g., {{source}}, {{destination}}).
Integrates with TLDR pages, RAG responses, and Streamlit interactive widgets.
"""

import re
from typing import Dict, List

PLACEHOLDER_REGEX = re.compile(r"\{\{([^}]+)\}\}")


def has_placeholders(text: str) -> bool:
    """Check if the text contains any {{placeholder}} tokens."""
    if not text:
        return False
    return bool(PLACEHOLDER_REGEX.search(text))


def extract_placeholders(text: str) -> List[str]:
    """
    Extract unique placeholder names from a template or text in order of appearance.

    Example:
        >>> extract_placeholders("cp {{source}} {{destination}}")
        ['source', 'destination']
        >>> extract_placeholders("grep {{pattern}} {{file}} {{pattern}}")
        ['pattern', 'file']
    """
    if not text:
        return []

    matches = PLACEHOLDER_REGEX.findall(text)
    seen = set()
    unique_placeholders = []
    for item in matches:
        clean = item.strip()
        if clean and clean not in seen:
            seen.add(clean)
            unique_placeholders.append(clean)
    return unique_placeholders


def find_command_templates(text: str) -> List[str]:
    """
    Locate candidate command lines or code snippets containing placeholders within text.

    Scans markdown code blocks, inline backticks, and lines containing '{{'.
    Returns a deduplicated list of template commands.
    """
    if not text or not has_placeholders(text):
        return []

    templates: List[str] = []
    seen = set()

    def add_candidate(cmd: str) -> None:
        cmd_clean = cmd.strip()
        if cmd_clean.startswith("`") and cmd_clean.endswith("`"):
            cmd_clean = cmd_clean.strip("`").strip()
        cmd_clean = re.sub(r"^[-*>\d.]+\s*", "", cmd_clean).strip()
        if cmd_clean and has_placeholders(cmd_clean) and cmd_clean not in seen:
            seen.add(cmd_clean)
            templates.append(cmd_clean)

    fenced_blocks = re.findall(
        r"```(?:[a-zA-Z0-9_-]+)?\s*[\r\n]+(.*?)\s*```",
        text,
        re.DOTALL | re.IGNORECASE,
    )
    for block in fenced_blocks:
        for line in block.splitlines():
            line_str = line.strip()
            if has_placeholders(line_str) and not line_str.startswith("#"):
                add_candidate(line_str)

    text_without_fences = re.sub(r"```.*?```", "", text, flags=re.DOTALL)

    inline_codes = re.findall(r"`([^`\r\n]+)`", text_without_fences)
    for inline in inline_codes:
        if has_placeholders(inline):
            add_candidate(inline)

    if not templates:
        for line in text.splitlines():
            line_str = line.strip()
            if has_placeholders(line_str):
                add_candidate(line_str)

    return templates


def fill_template(
    template: str,
    values: Dict[str, str],
    default_to_placeholder: bool = True,
) -> str:
    """
    Substitute placeholder tokens with user-supplied values.

    Args:
        template: The command string with {{placeholder}} markers.
        values: Mapping from placeholder names to replacement values.
        default_to_placeholder: If True, unfilled placeholders remain as {{name}}.
                                If False, unfilled placeholders are replaced with empty string.

    Returns:
        The instantiated command string.

    Example:
        >>> fill_template("cp {{source}} {{destination}}", {"source": "foo.txt", "destination": "bar.txt"})
        'cp foo.txt bar.txt'
    """
    if not template:
        return ""

    def replace_match(match: re.Match) -> str:
        key = match.group(1).strip()
        val = values.get(key)
        if val is not None and str(val).strip():
            return str(val).strip()
        return match.group(0) if default_to_placeholder else ""

    return PLACEHOLDER_REGEX.sub(replace_match, template)
