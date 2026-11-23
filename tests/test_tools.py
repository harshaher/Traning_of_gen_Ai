"""
test_tools.py - Unit Tests for Agent Tools and Command Utilities (Day 11 S1-E & S1-F)

Tests:
  1. chmod_calculator: Symbolic to Octal (e.g. rwxr-x--- -> 750).
  2. chmod_calculator: Octal to Symbolic (e.g. 750 -> rwxr-x---).
  3. chmod_calculator: Edge cases & invalid inputs.
  4. Destructive command safety checks.
  5. Signature Placeholder Filler utility.
"""

from app.placeholder import (
    extract_placeholders,
    fill_template,
    find_command_templates,
    has_placeholders,
)
from app.tools import check_destructive_command, chmod_calculator


def test_chmod_symbolic_to_octal_required():
    """Verify symbolic to octal conversion: rwxr-x--- -> 750."""
    res = chmod_calculator("rwxr-x---")
    assert res["valid"] is True
    assert res["octal"] == "750"
    assert res["symbolic"] == "rwxr-x---"
    assert "750" in res["explanation"]
    assert res["breakdown"]["owner"]["value"] == 7
    assert res["breakdown"]["group"]["value"] == 5
    assert res["breakdown"]["others"]["value"] == 0


def test_chmod_octal_to_symbolic_required():
    """Verify octal to symbolic conversion: 750 -> rwxr-x---."""
    res = chmod_calculator("750")
    assert res["valid"] is True
    assert res["symbolic"] == "rwxr-x---"
    assert res["octal"] == "750"
    assert "rwxr-x---" in res["explanation"]
    assert "read, write, execute" in res["owner_permissions"]
    assert "read, execute" in res["group_permissions"]
    assert "no permissions" in res["others_permissions"]


def test_chmod_standard_permutations():
    """Verify common permission codes: 777, 755, 644, 600, 400."""
    cases = [
        ("777", "rwxrwxrwx"),
        ("755", "rwxr-xr-x"),
        ("644", "rw-r--r--"),
        ("600", "rw-------"),
        ("400", "r--------"),
        ("000", "---------"),
    ]
    for octal, sym in cases:
        oct_res = chmod_calculator(octal)
        assert oct_res["valid"] is True
        assert oct_res["symbolic"] == sym

        sym_res = chmod_calculator(sym)
        assert sym_res["valid"] is True
        assert sym_res["octal"] == octal


def test_chmod_invalid_permission_inputs():
    """Verify safe error handling for malformed or out-of-range permissions."""
    invalid_cases = [
        "899",
        "75",
        "7555",
        "invalid",
        "rwxr-x--z",
        "rwxr-x",
        "",
        None,
    ]
    for bad_input in invalid_cases:
        res = chmod_calculator(bad_input)
        assert res["valid"] is False
        assert "error" in res


def test_check_destructive_command():
    """Verify destructive Linux command detection."""
    assert check_destructive_command("rm -rf /")["destructive"] is True
    assert check_destructive_command("rm -r myfolder")["destructive"] is True
    assert check_destructive_command("mkfs.ext4 /dev/sdb1")["destructive"] is True
    assert check_destructive_command("kill -9 1234")["destructive"] is True
    assert check_destructive_command("chmod 777 /var/www")["destructive"] is True
    assert check_destructive_command("ls -la /var/log")["destructive"] is False
    assert check_destructive_command("grep -rn 'hello' .")["destructive"] is False


def test_placeholder_filler_tools():
    """Verify placeholder extraction and command template filling."""
    template = "tar -xvf {{archive.tar.gz}} -C {{target_dir}}"
    assert has_placeholders(template) is True

    placeholders = extract_placeholders(template)
    assert placeholders == ["archive.tar.gz", "target_dir"]

    filled = fill_template(template, {"archive.tar.gz": "data.tar.gz", "target_dir": "/tmp"})
    assert filled == "tar -xvf data.tar.gz -C /tmp"

    doc = "Run command:\n```bash\ncp {{source}} {{destination}}\n```"
    templates = find_command_templates(doc)
    assert len(templates) == 1
    assert "cp {{source}} {{destination}}" in templates[0]
