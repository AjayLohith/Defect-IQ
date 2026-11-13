"""Unit tests for deliberate anomaly injection, ground truth separation, and detection."""
import csv
import json
import os
import pytest
from generator.src.validator import ValidationEngine

GT_JSON_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "artifacts", "ground_truth", "ground_truth.json"
)
GT_CSV_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "artifacts", "ground_truth", "ground_truth.csv"
)
DEFECTS_JSON_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "artifacts", "json", "defects.json"
)


def test_ground_truth_files_exist_and_segregated():
    """Verify ground truth exists strictly in artifacts/ground_truth/ and has required columns."""
    assert os.path.exists(GT_JSON_PATH), "ground_truth.json must exist"
    assert os.path.exists(GT_CSV_PATH), "ground_truth.csv must exist"

    with open(GT_JSON_PATH, "r", encoding="utf-8") as f:
        gt_data = json.load(f)

    assert len(gt_data) == 5, "Must have exactly 5 deliberate labelled anomalies"

    required_gt_fields = [
        "anomaly_id",
        "anomaly_type",
        "entity_type",
        "entity_id",
        "description",
        "expected_validator_rule",
        "injected_details",
    ]
    for anomaly in gt_data:
        for field in required_gt_fields:
            assert field in anomaly, f"Missing field {field} in ground truth record"

    # Verify that operational defects table does NOT contain ground_truth_label
    with open(DEFECTS_JSON_PATH, "r", encoding="utf-8") as f:
        defects = json.load(f)
    for d in defects:
        assert "ground_truth_label" not in d, "Operational Defect records must not expose ground_truth_label"


def test_validation_engine_detects_all_five_anomalies():
    """Verify that ValidationEngine detects all five injected anomalies with zero baseline failures."""
    engine = ValidationEngine()
    results = engine.run_all_checks()

    assert results["summary"]["failed_rules"] == 0, "All baseline rules must pass"
    assert results["summary"]["anomalies_detected"] == 5, "Must detect exactly 5 anomalies"

    detected_ids = {a["anomaly_id"] for a in results["detected_anomalies"]}
    expected_ids = {"ANOMALY-001", "ANOMALY-002", "ANOMALY-003", "ANOMALY-004", "ANOMALY-005"}
    assert detected_ids == expected_ids, f"Expected {expected_ids}, got {detected_ids}"

