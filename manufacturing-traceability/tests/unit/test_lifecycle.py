"""Unit tests for entity lifecycle transitions."""
import json
import os
import pytest

CONTRACT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "data_contract", "lifecycle_transitions", "transitions.json"
)


@pytest.fixture
def transitions_data():
    with open(CONTRACT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_material_lot_lifecycle_transitions(transitions_data):
    lot_rules = transitions_data["MaterialLot"]["transitions"]
    # Valid transitions
    assert "RELEASED" in lot_rules["RECEIVED"]
    assert "QUARANTINED" in lot_rules["RECEIVED"]
    assert "CONSUMED" in lot_rules["RELEASED"]
    assert "PARTIALLY_CONSUMED" in lot_rules["RELEASED"]

    # Invalid transitions
    assert "CONSUMED" not in lot_rules["RECEIVED"]
    assert "RECEIVED" not in lot_rules["CONSUMED"]


def test_production_order_lifecycle_transitions(transitions_data):
    order_rules = transitions_data["ProductionOrder"]["transitions"]
    # Valid transitions
    assert "RELEASED" in order_rules["PLANNED"]
    assert "IN_PROGRESS" in order_rules["RELEASED"]
    assert "COMPLETED" in order_rules["IN_PROGRESS"]
    assert "ON_HOLD" in order_rules["IN_PROGRESS"]
    assert "REWORK" in order_rules["IN_PROGRESS"]
    assert "SCRAPPED" in order_rules["IN_PROGRESS"]

    # Terminal states
    assert len(order_rules["COMPLETED"]) == 0
    assert len(order_rules["SCRAPPED"]) == 0


def test_capa_closure_lifecycle_gate(transitions_data):
    capa_rules = transitions_data["CorrectiveAction"]["transitions"]
    # Valid flow
    assert "IMPLEMENTED" in capa_rules["OPEN"]
    assert "VERIFICATION_PENDING" in capa_rules["IMPLEMENTED"]
    assert "VERIFIED" in capa_rules["VERIFICATION_PENDING"]
    assert "CLOSED" in capa_rules["VERIFIED"]

    # Closure can ONLY happen from VERIFIED
    assert "CLOSED" not in capa_rules["OPEN"]
    assert "CLOSED" not in capa_rules["IMPLEMENTED"]
    assert "CLOSED" not in capa_rules["VERIFICATION_PENDING"]

