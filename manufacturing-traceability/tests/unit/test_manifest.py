"""Unit tests for source_manifest.json compliance and row_count validation."""
import json
import os
import pytest

MANIFEST_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "artifacts", "manifest", "source_manifest.json"
)


def test_manifest_structure_and_row_counts():
    """Verify that source_manifest.json contains logical row_count and diagnostic line_count."""
    assert os.path.exists(MANIFEST_PATH), "source_manifest.json must exist"
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert "manifest_version" in manifest
    assert "master_seed" in manifest
    assert manifest["master_seed"] == 20261022
    assert "dataset_profile" in manifest
    assert "table_row_counts" in manifest
    assert "files" in manifest

    # Check each tracked file has row_count, line_count, sha256, size_bytes
    for file_key, file_meta in manifest["files"].items():
        assert "row_count" in file_meta, f"File {file_key} must have row_count"
        assert "line_count" in file_meta, f"File {file_key} must retain line_count"
        assert "sha256" in file_meta, f"File {file_key} must have sha256"
        assert "size_bytes" in file_meta, f"File {file_key} must have size_bytes"

        assert isinstance(file_meta["row_count"], int)
        assert isinstance(file_meta["line_count"], int)
        assert file_meta["row_count"] >= 0
        assert file_meta["line_count"] >= 0

    # Verify table row counts consistency
    table_counts = manifest["table_row_counts"]
    assert table_counts.get("products") == 20
    assert table_counts.get("suppliers") == 10
    assert table_counts.get("material_lots") == 100
    assert table_counts.get("production_orders") == 200

