"""Unit tests for deterministic zero-padded ID generators."""
import re
import pytest
from generator.src.ids import (
    format_sku_id,
    format_supplier_id,
    format_lot_id,
    format_order_id,
    format_inspection_id,
    format_defect_id,
    format_capa_id,
    format_containment_id,
    format_verification_id,
    format_event_id,
    format_bom_id,
    format_bom_line_id,
    format_consumption_id,
    format_machine_id,
    format_process_step_id,
    format_process_execution_id,
    format_inspection_plan_id,
)


def test_sku_id_format():
    val = format_sku_id(1)
    assert val == "SKU-000001"
    assert re.match(r"^SKU-\d{6}$", val)

    val_large = format_sku_id(200)
    assert val_large == "SKU-000200"


def test_supplier_id_format():
    val = format_supplier_id(1)
    assert val == "SUP-0001"
    assert re.match(r"^SUP-\d{4}$", val)


def test_material_lot_id_format():
    val = format_lot_id(1, 2026, 1)
    assert val == "LOT-SUP-0001-2026-000001"
    assert re.match(r"^LOT-SUP-\d{4}-\d{4}-\d{6}$", val)

    val2 = format_lot_id(15, 2026, 942)
    assert val2 == "LOT-SUP-0015-2026-000942"


def test_production_order_id_format():
    val = format_order_id(2026, 1)
    assert val == "WO-2026-000001"
    assert re.match(r"^WO-\d{4}-\d{6}$", val)


def test_inspection_id_format():
    val = format_inspection_id(2026, 1, 1)
    assert val == "INSP-WO-2026-000001-001"
    assert re.match(r"^INSP-WO-\d{4}-\d{6}-\d{3}$", val)


def test_defect_id_format():
    val = format_defect_id(2026, 1)
    assert val == "DEF-2026-000001"
    assert re.match(r"^DEF-\d{4}-\d{6}$", val)


def test_capa_id_format():
    val = format_capa_id(2026, 1)
    assert val == "CAPA-2026-000001"
    assert re.match(r"^CAPA-\d{4}-\d{6}$", val)


def test_containment_and_verification_id_formats():
    assert format_containment_id(2026, 1) == "CNT-2026-000001"
    assert format_verification_id(2026, 1) == "VERIF-2026-000001"
    assert format_event_id(1) == "EVT-00000001"
    assert format_bom_id(1) == "BOM-000001"
    assert format_bom_line_id(1) == "BOML-000001"
    assert format_consumption_id(1) == "CONS-000001"
    assert format_machine_id(1) == "MCH-0001"
    assert format_process_step_id(1) == "STEP-0001"
    assert format_process_execution_id(1) == "PEX-000001"
    assert format_inspection_plan_id(1) == "PLAN-0001"

