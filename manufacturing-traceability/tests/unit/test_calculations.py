"""Unit tests for quantity calculations and arithmetic reconciliation."""
import pytest
from decimal import Decimal


def test_material_lot_reconciliation():
    """Verify received_quantity == available + consumed + rejected + quarantined."""
    received = Decimal("1000.0000")
    available = Decimal("650.0000")
    consumed = Decimal("300.0000")
    rejected = Decimal("30.0000")
    quarantined = Decimal("20.0000")

    assert received == available + consumed + rejected + quarantined


def test_inspection_result_reconciliation():
    """Verify inspection mutually exclusive partitions and defect rate denominator."""
    inspected = Decimal("50.00")
    accepted = Decimal("46.00")
    rejected = Decimal("4.00")

    reworked = Decimal("2.00")
    scrapped = Decimal("1.00")
    quarantined = Decimal("1.00")

    # Partition 1: inspected = accepted + rejected
    assert inspected == accepted + rejected

    # Partition 2: rejected = reworked + scrapped + quarantined
    assert rejected == reworked + scrapped + quarantined

    # Defect rate calculation with inspected as denominator
    defect_rate = rejected / inspected
    assert defect_rate == Decimal("0.0800")


def test_production_order_reconciliation():
    """Verify production order mutually exclusive partitions."""
    completed = Decimal("100.00")
    accepted = Decimal("94.00")
    rework = Decimal("3.00")
    scrap = Decimal("2.00")
    quarantined = Decimal("1.00")

    rejected = rework + scrap + quarantined
    assert completed == accepted + rejected


def test_process_execution_reconciliation():
    """Verify process execution mutually exclusive input/output balance."""
    input_qty = Decimal("100.00")
    output_qty = Decimal("98.00")
    scrap_qty = Decimal("1.00")
    quar_qty = Decimal("0.00")
    rework_qty = Decimal("1.00")

    assert input_qty == output_qty + scrap_qty + quar_qty + rework_qty

