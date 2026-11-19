"""
test_records.py - Unit Tests for Linux Command Record Management (Day 11 S1-A)

Tests:
  1. Loading records successfully from dataset.
  2. Verifying required record schema and fields.
  3. Handling empty, non-existent, or corrupted datasets safely.
  4. Lookup by ID and command name.
  5. Category groupings and aggregations.
"""

from pathlib import Path

from app.records import count_by, get_by_id, load_records, search


def test_load_records_success():
    """Verify that records are successfully loaded from data/records.json."""
    records = load_records()
    assert isinstance(records, list)
    assert len(records) >= 20, f"Expected at least 20 records, found {len(records)}"

    unique_commands = {r["command"] for r in records if "command" in r}
    assert len(unique_commands) >= 20, f"Expected >= 20 unique commands, got {len(unique_commands)}"
    assert "grep" in unique_commands
    assert "chmod" in unique_commands
    assert "tar" in unique_commands


def test_records_required_fields():
    """Verify that every record contains the required metadata attributes."""
    records = load_records()
    required_fields = {
        "command",
        "platform",
        "description",
        "example_task",
        "example_command",
        "source_url",
        "id",
        "category",
    }

    for record in records:
        missing = required_fields - set(record.keys())
        assert not missing, f"Record for '{record.get('command')}' is missing fields: {missing}"
        assert isinstance(record["id"], int)
        assert len(record["command"].strip()) > 0
        assert len(record["description"].strip()) > 0


def test_records_nonexistent_file_handling(tmp_path: Path):
    """Verify that loading a non-existent path gracefully returns an empty list."""
    non_existent = tmp_path / "does_not_exist.json"
    result = load_records(non_existent)
    assert result == []


def test_records_get_by_id_and_command():
    """Verify record retrieval by integer ID, string digit, and command name."""
    records = load_records()
    assert len(records) > 0

    first_record = records[0]
    rec_by_int = get_by_id(records, 1)
    assert rec_by_int is not None
    assert rec_by_int["id"] == 1

    rec_by_str_id = get_by_id(records, "1")
    assert rec_by_str_id == rec_by_int

    rec_by_name = get_by_id(records, first_record["command"])
    assert rec_by_name is not None
    assert rec_by_name["command"].lower() == first_record["command"].lower()


def test_records_get_by_id_missing():
    """Verify that invalid or missing IDs return None without errors."""
    records = load_records()
    assert get_by_id(records, 999999) is None
    assert get_by_id(records, "unknown_ghost_command") is None
    assert get_by_id([], 1) is None


def test_records_count_by_category():
    """Verify grouping and counting records by category."""
    records = load_records()
    counts = count_by(records, "category")
    assert isinstance(counts, dict)
    assert sum(counts.values()) == len(records)
    assert "Permissions" in counts or "Search & Pattern" in counts

    # Test empty input
    assert count_by([], "category") == {}


def test_records_search_empty_and_missing_data():
    """Verify search handles empty keywords and empty record lists safely."""
    records = load_records()
    assert search(records, "") == []
    assert search(records, "   ") == []
    assert search([], "grep") == []
