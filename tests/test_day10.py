"""
test_day10.py - Unit & Integration Tests for Day 10:
  - Signature Feature: Placeholder extraction, command template parsing, and interactive fill logic.
  - Feedback Endpoint: POST /feedback and GET /feedback persistence.
  - Streamlit UI Helper integration.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.placeholder import (
    extract_placeholders,
    fill_template,
    find_command_templates,
    has_placeholders,
)

client = TestClient(app)


def test_placeholder_has_placeholders():
    """Verify detection of {{placeholder}} tokens."""
    assert has_placeholders("cp {{source}} {{destination}}") is True
    assert has_placeholders("`chmod {{mode}} {{file}}`") is True
    assert has_placeholders("ls -la /var/log") is False
    assert has_placeholders("{not_a_double_brace}") is False
    assert has_placeholders("") is False


def test_placeholder_extraction_basic_and_deduplication():
    """Verify unique placeholder extraction preserving ordering."""
    text = "grep {{search_pattern}} {{file1}} {{file2}} {{search_pattern}}"
    placeholders = extract_placeholders(text)
    assert placeholders == ["search_pattern", "file1", "file2"]


def test_placeholder_extraction_whitespace_trimming():
    """Verify placeholders with internal whitespace are trimmed properly."""
    text = "tar -czvf {{ archive.tar.gz }} {{  directory  }}"
    placeholders = extract_placeholders(text)
    assert placeholders == ["archive.tar.gz", "directory"]


def test_placeholder_template_detection_fenced_and_inline():
    """Verify extracting commands from markdown code blocks and inline code."""
    markdown_content = (
        "Here is how you extract an archive:\n"
        "```bash\n"
        "tar -xvf {{archive.tar.gz}} -C {{target_dir}}\n"
        "```\n"
        "Or check permissions using `chmod {{mode}} {{path/to/file}}`."
    )
    templates = find_command_templates(markdown_content)
    assert len(templates) >= 2
    assert any("tar -xvf {{archive.tar.gz}}" in t for t in templates)
    assert any("chmod {{mode}}" in t for t in templates)


def test_placeholder_template_detection_bullet_list():
    """Verify bulleted command templates without code blocks are detected."""
    raw_text = "- `chmod u+x {{path/to/file}}`\n- `ls {{[-la|-l]}}`"
    templates = find_command_templates(raw_text)
    assert len(templates) >= 2
    assert templates[0] == "chmod u+x {{path/to/file}}"


def test_placeholder_fill_complete():
    """Verify complete placeholder substitution."""
    template = "cp -r {{source_dir}} {{destination_dir}}"
    values = {
        "source_dir": "/home/user/docs",
        "destination_dir": "/backup/docs",
    }
    result = fill_template(template, values)
    assert result == "cp -r /home/user/docs /backup/docs"


def test_placeholder_fill_partial_and_default():
    """Verify unfilled placeholders are kept when default_to_placeholder=True."""
    template = "curl -X {{method}} {{url}} -d '{{payload}}'"
    values = {"method": "POST", "url": "https://api.example.com"}

    result = fill_template(template, values, default_to_placeholder=True)
    assert result == "curl -X POST https://api.example.com -d '{{payload}}'"

    result_empty = fill_template(template, values, default_to_placeholder=False)
    assert result_empty == "curl -X POST https://api.example.com -d ''"


def test_placeholder_fill_empty_template():
    """Verify empty template returns empty string."""
    assert fill_template("", {"foo": "bar"}) == ""


def test_feedback_submit_helpful():
    """Verify POST /feedback records a helpful rating."""
    payload = {
        "question": "How do I list hidden files?",
        "answer": "Use `ls -a` to include directory entries whose names begin with a dot.",
        "rating": "helpful",
        "thread_id": "test_user_stream",
    }
    response = client.post("/feedback", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["total_feedback"] >= 1


def test_feedback_submit_not_helpful():
    """Verify POST /feedback records a not_helpful rating."""
    payload = {
        "question": "Tell me a joke",
        "answer": "I am ShellSathi, a Linux assistant.",
        "rating": "not_helpful",
        "thread_id": "test_user_stream_2",
    }
    response = client.post("/feedback", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"


def test_feedback_invalid_rating():
    """Verify POST /feedback rejects invalid rating values."""
    payload = {
        "question": "How to grep?",
        "answer": "Use grep.",
        "rating": "neutral_maybe",
    }
    response = client.post("/feedback", json=payload)
    assert response.status_code == 422


def test_feedback_get_summary_and_persistence():
    """Verify GET /feedback returns recorded entries and statistics."""
    response = client.get("/feedback")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "helpful" in data
    assert "not_helpful" in data
    assert isinstance(data["feedback"], list)
    assert data["total"] == data["helpful"] + data["not_helpful"]


def test_ui_app_imports_and_helpers():
    """Verify ui/app.py components and helpers can be imported and executed."""
    from ui.app import check_backend_health, send_agent_request, send_ask_request

    assert callable(check_backend_health)
    assert callable(send_ask_request)
    assert callable(send_agent_request)


if __name__ == "__main__":
    pytest.main(["-v", __file__])
