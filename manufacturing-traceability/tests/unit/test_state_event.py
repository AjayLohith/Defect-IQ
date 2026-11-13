"""Unit tests for StateEvent foreign-key integrity validation."""
from datetime import datetime, timezone
import pytest
from backend.app.models.event import StateEvent
from backend.app.schemas.event import StateEventCreate


def test_state_event_valid_mappings():
    """Verify that each valid entity_type with exactly matching FK passes validation."""
    now = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    # 1. MATERIAL_LOT
    evt_lot = StateEvent(
        event_id="EVT-00000001",
        entity_type="MATERIAL_LOT",
        entity_id="LOT-SUP-0001-2026-000001",
        material_lot_id="LOT-SUP-0001-2026-000001",
        event_sequence=1,
        new_state="RECEIVED",
        event_timestamp=now,
    )
    evt_lot.validate_integrity()

    pyd_lot = StateEventCreate(
        event_id="EVT-00000001",
        entity_type="MATERIAL_LOT",
        entity_id="LOT-SUP-0001-2026-000001",
        material_lot_id="LOT-SUP-0001-2026-000001",
        event_sequence=1,
        new_state="RECEIVED",
        event_timestamp=now,
    )
    assert pyd_lot.material_lot_id == "LOT-SUP-0001-2026-000001"

    # 2. DEFECT
    evt_defect = StateEvent(
        event_id="EVT-00000002",
        entity_type="DEFECT",
        entity_id="DEF-2026-000001",
        defect_id="DEF-2026-000001",
        event_sequence=1,
        new_state="OPEN",
        event_timestamp=now,
    )
    evt_defect.validate_integrity()

    # 3. PRODUCTION_ORDER
    evt_order = StateEvent(
        event_id="EVT-00000003",
        entity_type="PRODUCTION_ORDER",
        entity_id="WO-2026-000001",
        production_order_id="WO-2026-000001",
        event_sequence=1,
        new_state="PLANNED",
        event_timestamp=now,
    )
    evt_order.validate_integrity()

    # 4. INSPECTION_RESULT
    evt_insp = StateEvent(
        event_id="EVT-00000004",
        entity_type="INSPECTION_RESULT",
        entity_id="INSP-WO-2026-000001-001",
        inspection_result_id="INSP-WO-2026-000001-001",
        event_sequence=1,
        new_state="COMPLETED",
        event_timestamp=now,
    )
    evt_insp.validate_integrity()

    # 5. CORRECTIVE_ACTION
    evt_capa = StateEvent(
        event_id="EVT-00000005",
        entity_type="CORRECTIVE_ACTION",
        entity_id="CAPA-2026-000001",
        corrective_action_id="CAPA-2026-000001",
        event_sequence=1,
        new_state="OPEN",
        event_timestamp=now,
    )
    evt_capa.validate_integrity()


def test_state_event_invalid_cross_entity_mapping():
    """Verify that populating a foreign key belonging to another entity raises ValueError."""
    now = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    # entity_type = DEFECT but populated production_order_id
    evt = StateEvent(
        event_id="EVT-00000010",
        entity_type="DEFECT",
        entity_id="DEF-2026-000001",
        production_order_id="WO-2026-000001",
        event_sequence=1,
        new_state="OPEN",
        event_timestamp=now,
    )
    with pytest.raises(ValueError, match="corresponding foreign key must be populated"):
        evt.validate_integrity()

    with pytest.raises(ValueError):
        StateEventCreate(
            event_id="EVT-00000010",
            entity_type="DEFECT",
            entity_id="DEF-2026-000001",
            production_order_id="WO-2026-000001",
            event_sequence=1,
            new_state="OPEN",
            event_timestamp=now,
        )


def test_state_event_id_mismatch():
    """Verify that entity_id not matching the typed foreign key raises ValueError."""
    now = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    evt = StateEvent(
        event_id="EVT-00000011",
        entity_type="DEFECT",
        entity_id="DEF-2026-000001",
        defect_id="DEF-2026-999999",  # mismatched ID
        event_sequence=1,
        new_state="OPEN",
        event_timestamp=now,
    )
    with pytest.raises(ValueError, match="equal entity_id"):
        evt.validate_integrity()

    with pytest.raises(ValueError):
        StateEventCreate(
            event_id="EVT-00000011",
            entity_type="DEFECT",
            entity_id="DEF-2026-000001",
            defect_id="DEF-2026-999999",
            event_sequence=1,
            new_state="OPEN",
            event_timestamp=now,
        )


def test_state_event_multiple_foreign_keys():
    """Verify that populating more than one foreign key raises ValueError."""
    now = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    evt = StateEvent(
        event_id="EVT-00000012",
        entity_type="DEFECT",
        entity_id="DEF-2026-000001",
        defect_id="DEF-2026-000001",
        material_lot_id="LOT-SUP-0001-2026-000001",  # extra FK
        event_sequence=1,
        new_state="OPEN",
        event_timestamp=now,
    )
    with pytest.raises(ValueError, match="must be NULL when entity_type is 'DEFECT'"):
        evt.validate_integrity()

    with pytest.raises(ValueError):
        StateEventCreate(
            event_id="EVT-00000012",
            entity_type="DEFECT",
            entity_id="DEF-2026-000001",
            defect_id="DEF-2026-000001",
            material_lot_id="LOT-SUP-0001-2026-000001",
            event_sequence=1,
            new_state="OPEN",
            event_timestamp=now,
        )

