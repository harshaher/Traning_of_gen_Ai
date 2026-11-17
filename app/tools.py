"""
tools.py - ShellSathi Agent Tools: chmod Calculator and Safety Checker (Day 9)
Provides Linux file permission calculation and destructive command verification.
"""

import re
from typing import Any, Dict, Optional

# Standard permission maps
OCTAL_TO_SYM = {
    0: "---",
    1: "--x",
    2: "-w-",
    3: "-wx",
    4: "r--",
    5: "r-x",
    6: "rw-",
    7: "rwx",
}

SYM_TO_OCTAL = {v: k for k, v in OCTAL_TO_SYM.items()}


def _describe_permissions(value: int) -> str:
    """Return beginner-friendly human-readable permission description."""
    parts = []
    if value & 4:
        parts.append("read")
    if value & 2:
        parts.append("write")
    if value & 1:
        parts.append("execute")
    return ", ".join(parts) if parts else "no permissions"


def chmod_calculator(permission: Any) -> Dict[str, Any]:
    """
    Linux file permission calculator converting in both directions:
      - Symbolic to Octal (e.g. 'rwxr-x---' -> '750')
      - Octal to Symbolic (e.g. '750' -> 'rwxr-x---')
    Returns a structured dictionary with breakdowns and human-readable explanation.
    """
    if permission is None:
        return {
            "valid": False,
            "error": "Empty input. Please provide a permission string.",
            "input_permission": "",
        }

    raw = str(permission).strip()
    if not raw:
        return {
            "valid": False,
            "error": "Empty input. Please provide a permission string.",
            "input_permission": raw,
        }

    # Case 1: Octal input (3 digits between 0 and 7, e.g. 750, 755, 600, 644)
    if re.fullmatch(r"[0-7]{3}", raw):
        d_owner = int(raw[0])
        d_group = int(raw[1])
        d_others = int(raw[2])

        sym_owner = OCTAL_TO_SYM[d_owner]
        sym_group = OCTAL_TO_SYM[d_group]
        sym_others = OCTAL_TO_SYM[d_others]
        symbolic = f"{sym_owner}{sym_group}{sym_others}"

        owner_desc = _describe_permissions(d_owner)
        group_desc = _describe_permissions(d_group)
        others_desc = _describe_permissions(d_others)

        explanation = (
            f"Octal permission {raw} converts to symbolic '{symbolic}'.\n"
            f"- Owner: {owner_desc}\n"
            f"- Group: {group_desc}\n"
            f"- Others: {others_desc}"
        )

        return {
            "valid": True,
            "input": raw,
            "input_permission": raw,
            "input_type": "octal",
            "converted_permission": symbolic,
            "octal": raw,
            "symbolic": symbolic,
            "owner_permissions": owner_desc,
            "group_permissions": group_desc,
            "others_permissions": others_desc,
            "explanation": explanation,
            "breakdown": {
                "owner": {
                    "entity": "Owner (User)",
                    "value": d_owner,
                    "summary": owner_desc,
                    "read": bool(d_owner & 4),
                    "write": bool(d_owner & 2),
                    "execute": bool(d_owner & 1),
                },
                "group": {
                    "entity": "Group",
                    "value": d_group,
                    "summary": group_desc,
                    "read": bool(d_group & 4),
                    "write": bool(d_group & 2),
                    "execute": bool(d_group & 1),
                },
                "others": {
                    "entity": "Others",
                    "value": d_others,
                    "summary": others_desc,
                    "read": bool(d_others & 4),
                    "write": bool(d_others & 2),
                    "execute": bool(d_others & 1),
                },
            },
        }

    # Case 2: Symbolic input (9 characters consisting of r, w, x, -)
    if re.fullmatch(r"[rwx\-]{9}", raw):
        t_owner = raw[0:3]
        t_group = raw[3:6]
        t_others = raw[6:9]

        def _triplet_value(t: str) -> Optional[int]:
            r = 4 if t[0] == "r" else (0 if t[0] == "-" else -1)
            w = 2 if t[1] == "w" else (0 if t[1] == "-" else -1)
            x = 1 if t[2] == "x" else (0 if t[2] == "-" else -1)
            if r == -1 or w == -1 or x == -1:
                return None
            return r + w + x

        d_owner = _triplet_value(t_owner)
        d_group = _triplet_value(t_group)
        d_others = _triplet_value(t_others)

        if d_owner is None or d_group is None or d_others is None:
            return {
                "valid": False,
                "error": f"Invalid symbolic triplet format in '{raw}'. Standard positions are r, w, x or -.",
                "input_permission": raw,
            }

        octal = f"{d_owner}{d_group}{d_others}"
        owner_desc = _describe_permissions(d_owner)
        group_desc = _describe_permissions(d_group)
        others_desc = _describe_permissions(d_others)

        explanation = (
            f"Symbolic permission '{raw}' converts to octal {octal}.\n"
            f"- Owner: {owner_desc}\n"
            f"- Group: {group_desc}\n"
            f"- Others: {others_desc}"
        )

        return {
            "valid": True,
            "input": raw,
            "input_permission": raw,
            "input_type": "symbolic",
            "converted_permission": octal,
            "octal": octal,
            "symbolic": raw,
            "owner_permissions": owner_desc,
            "group_permissions": group_desc,
            "others_permissions": others_desc,
            "explanation": explanation,
            "breakdown": {
                "owner": {
                    "entity": "Owner (User)",
                    "value": d_owner,
                    "summary": owner_desc,
                    "read": bool(d_owner & 4),
                    "write": bool(d_owner & 2),
                    "execute": bool(d_owner & 1),
                },
                "group": {
                    "entity": "Group",
                    "value": d_group,
                    "summary": group_desc,
                    "read": bool(d_group & 4),
                    "write": bool(d_group & 2),
                    "execute": bool(d_group & 1),
                },
                "others": {
                    "entity": "Others",
                    "value": d_others,
                    "summary": others_desc,
                    "read": bool(d_others & 4),
                    "write": bool(d_others & 2),
                    "execute": bool(d_others & 1),
                },
            },
        }

    # Case 3: Invalid input format
    if len(raw) == 3 and any(ch not in "01234567" for ch in raw):
        error_msg = f"Invalid octal permission '{raw}'. Octal digits must be between 0 and 7."
    elif len(raw) == 9 and any(ch not in "rwx-" for ch in raw):
        error_msg = f"Invalid symbolic permission '{raw}'. Characters must only be 'r', 'w', 'x', or '-'."
    elif len(raw) not in (3, 9):
        error_msg = (
            f"Invalid permission length ({len(raw)} characters). "
            "Expected a 3-digit octal (e.g. '750') or a 9-character symbolic string (e.g. 'rwxr-x---')."
        )
    else:
        error_msg = (
            f"Invalid permission format '{raw}'. "
            "Please provide a 3-digit octal (000-777) or a 9-character symbolic string."
        )

    return {
        "valid": False,
        "error": error_msg,
        "input_permission": raw,
        "input": raw,
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
