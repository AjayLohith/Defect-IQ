"""Contract tests for data contracts, vocabularies, and schema tables."""
import json
import os
import pytest

VOCAB_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "data_contract", "controlled_vocabularies", "enums.json"
)
SCHEMA_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "data_contract", "schema", "tables.json"
)


def test_controlled_vocabularies_exist():
    assert os.path.exists(VOCAB_PATH), "enums.json must exist"
    with open(VOCAB_PATH, "r", encoding="utf-8") as f:
        vocab = json.load(f)

    required_enums = [
        "ProductType",
        "SupplierRiskTier",
        "MaterialLotStatus",
        "OrderStatus",
        "MachineType",
        "InspectionDisposition",
        "DefectSeverity",
        "DefectStatus",
        "CAPAStatus",
        "VerificationResult",
        "EntityType",
    ]
    for en in required_enums:
        assert en in vocab, f"Enum {en} must be present in controlled vocabularies"
        assert len(vocab[en]) > 0


def test_schema_tables_contract():
    assert os.path.exists(SCHEMA_PATH), "tables.json must exist"
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = json.load(f)

    required_tables = [
        "products",
        "boms",
        "bom_lines",
        "suppliers",
        "material_lots",
        "production_orders",
        "material_consumptions",
        "machines",
        "process_steps",
        "process_executions",
        "inspection_plans",
        "inspection_results",
        "defects",
        "containment_actions",
        "corrective_actions",
        "capa_verifications",
        "state_events",
    ]
    assert "tables" in schema
    for t in required_tables:
        assert t in schema["tables"], f"Table {t} must be defined in schema tables contract"
        assert "columns" in schema["tables"][t]

