"""
tools.py - ShellSathi Agent Tools: chmod Calculator and Safety Checker (Day 9)
"""

import re
from typing import Any, Dict, Optional


def chmod_calculator(input_perm: str) -> Dict[str, Any]:
    """
    Complete chmod permission converter and validator:
      - Converts symbolic to octal (e.g. rwxr-x--- -> 750)
      - Converts octal to symbolic (e.g. 750 -> rwxr-x---)
      - Breaks down permissions into Owner, Group, Others
      - Validates and handles invalid inputs
    """
    raw = str(input_perm).strip()
    if not raw:
        return {"valid": False, "error": "Empty permission input."}

    # Case A: Octal input (3 digits, each 0-7, e.g. 750, 644, 777)
    if re.fullmatch(r"[0-7]{3}", raw):
        digits = [int(d) for d in raw]

        def _digit_to_sym(d: int) -> str:
            r = "r" if (d & 4) else "-"
            w = "w" if (d & 2) else "-"
            x = "x" if (d & 1) else "-"
            return f"{r}{w}{x}"

        symbolic = "".join(_digit_to_sym(d) for d in digits)
        octal = raw

        breakdown = {
            "owner": _explain_digit(digits[0], "Owner (User)"),
            "group": _explain_digit(digits[1], "Group"),
            "others": _explain_digit(digits[2], "Others"),
        }

        return {
            "valid": True,
            "input": raw,
            "input_type": "octal",
            "octal": octal,
            "symbolic": symbolic,
            "explanation": f"Octal {octal} corresponds to symbolic '{symbolic}'.",
            "breakdown": breakdown,
        }

    # Case B: Symbolic input (9 characters, only r, w, x, -, e.g. rwxr-x---)
    if re.fullmatch(r"[rwx\-]{9}", raw):
        triplets = [raw[0:3], raw[3:6], raw[6:9]]

        def _triplet_to_digit(t: str) -> int:
            val = 0
            if t[0] == "r":
                val += 4
            if t[1] == "w":
                val += 2
            if t[2] == "x":
                val += 1
            return val

        digits = [_triplet_to_digit(t) for t in triplets]
        octal = "".join(str(d) for d in digits)
        symbolic = raw

        breakdown = {
            "owner": _explain_digit(digits[0], "Owner (User)"),
            "group": _explain_digit(digits[1], "Group"),
            "others": _explain_digit(digits[2], "Others"),
        }

        return {
            "valid": True,
            "input": raw,
            "input_type": "symbolic",
            "octal": octal,
            "symbolic": symbolic,
            "explanation": f"Symbolic '{symbolic}' corresponds to octal {octal}.",
            "breakdown": breakdown,
        }

    # Case C: Invalid input
    return {
        "valid": False,
        "input": raw,
        "error": (
            f"Invalid permission format '{raw}'. "
            "Please provide either a 3-digit octal value (e.g. '750', '644') "
            "or a 9-character symbolic string (e.g. 'rwxr-x---', 'rw-r--r--')."
        ),
    }


def _explain_digit(d: int, entity: str) -> Dict[str, Any]:
    """Explain permissions for a single digit (0-7)."""
    perms = []
    if d & 4:
        perms.append("Read (4)")
    if d & 2:
        perms.append("Write (2)")
    if d & 1:
        perms.append("Execute (1)")

    summary = ", ".join(perms) if perms else "No permissions (0)"
    return {
        "entity": entity,
        "value": d,
        "summary": summary,
        "read": bool(d & 4),
        "write": bool(d & 2),
        "execute": bool(d & 1),
    }


def check_destructive_command(command_str: str) -> Dict[str, Any]:
    """Check if a Linux command poses destructive risk requiring confirmation."""
    cmd = command_str.lower().strip()
    destructive_patterns = [
        (r"\brm\s+(-[rfRF]+\s+|.*\*|/)", "rm command can recursively or permanently delete files."),
        (r"\bmkfs\b", "mkfs creates a filesystem and destroys existing drive data."),
        (r"\bdd\b", "dd can overwrite disk partitions directly."),
        (r"\bkill\s+-9\b", "kill -9 forcefully terminates processes without saving state."),
        (r"\bchmod\s+(-R\s+)?777\b", "chmod 777 grants full world-writable access, posing a major security risk."),
    ]

    for pattern, warning in destructive_patterns:
        if re.search(pattern, cmd):
            return {
                "destructive": True,
                "warning": warning,
                "approval_required": True,
            }

    return {"destructive": False, "warning": "", "approval_required": False}
