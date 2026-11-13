"""Integration tests for deterministic generator output and dataset integrity."""
import os
import json
import pytest
from generator.src.config import MASTER_SEED, get_profile
from generator.src.master_data import generate_master_data
from generator.src.transactions import generate_transactions
from generator.src.outcomes import generate_outcomes_and_defects
from generator.src.anomalies import inject_anomalies


def test_generator_starter_profile_volume_and_joins():
    """Verify generated dataset volumes and baseline join validity."""
    profile = get_profile("starter")
    master = generate_master_data(profile, MASTER_SEED)
    trans = generate_transactions(master, profile, MASTER_SEED)
    outcomes = generate_outcomes_and_defects(master, trans, MASTER_SEED)

    assert len(master["products"]) == 20
    assert len(master["suppliers"]) == 10
    assert len(trans["material_lots"]) == 100
    assert len(trans["production_orders"]) == 200
    assert len(trans["inspection_results"]) == 800  # 200 orders * 4 quality gate steps
    assert len(outcomes["defects"]) > 0
    assert len(outcomes["containment_actions"]) > 0
    assert len(outcomes["corrective_actions"]) > 0
    assert len(outcomes["capa_verifications"]) > 0
    assert len(outcomes["state_events"]) > 0

    # Test baseline joins
    prod_ids = {p["product_id"] for p in master["products"]}
    supp_ids = {s["supplier_id"] for s in master["suppliers"]}
    lot_ids = {l["material_lot_id"] for l in trans["material_lots"]}
    order_ids = {o["production_order_id"] for o in trans["production_orders"]}

    for lot in trans["material_lots"]:
        assert lot["supplier_id"] in supp_ids
        assert lot["material_product_id"] in prod_ids

    for order in trans["production_orders"]:
        assert order["product_id"] in prod_ids

    for cons in trans["material_consumptions"]:
        assert cons["production_order_id"] in order_ids
        assert cons["material_lot_id"] in lot_ids

