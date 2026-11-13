"""Deliberate anomaly injector and separate ground truth generator.

Injects exactly five safe anomalies into baseline data without corrupting database foreign-key constraints.
Writes authoritative labels exclusively to artifacts/ground_truth/.
"""
import copy
from typing import Dict, List, Any, Tuple
from generator.src.ids import format_event_id


def inject_anomalies(dataset: Dict[str, List[Dict[str, Any]]]) -> Tuple[Dict[str, List[Dict[str, Any]]], List[Dict[str, Any]]]:
    """Injects five deliberate anomalies and creates isolated ground truth records."""
    modified_dataset = copy.deepcopy(dataset)
    ground_truth: List[Dict[str, Any]] = []

    defects = modified_dataset["defects"]
    orders = modified_dataset["production_orders"]
    consumptions = modified_dataset["material_consumptions"]
    capas = modified_dataset["corrective_actions"]
    verifications = modified_dataset["capa_verifications"]
    events = modified_dataset["state_events"]
    inspections = modified_dataset["inspection_results"]
    executions = modified_dataset["process_executions"]

    max_event_seq = max((e["event_sequence"] for e in events), default=1)
    total_events_count = len(events)

    # -------------------------------------------------------------
    # Scenario 1: Defect with nonexistent reported material lot ID
    # -------------------------------------------------------------
    if defects:
        target_defect = defects[0]
        original_lot = target_defect["material_lot_id"]
        target_defect["material_lot_id"] = None
        target_defect["reported_material_lot_id"] = "LOT-SUP-9999-2026-999999"
        target_defect["supplier_id"] = None

        ground_truth.append({
            "anomaly_id": "ANOMALY-001",
            "anomaly_type": "NONEXISTENT_REPORTED_LOT",
            "entity_type": "DEFECT",
            "entity_id": target_defect["defect_id"],
            "description": "Defect reported with material lot ID LOT-SUP-9999-2026-999999 that does not exist in inventory.",
            "expected_validator_rule": "VAL_DEFECT_REPORTED_LOT_EXISTS",
            "injected_details": f"Original lot {original_lot} cleared to NULL; raw reported set to LOT-SUP-9999-2026-999999.",
        })

    # -------------------------------------------------------------
    # Scenario 2: Completed order missing BOM-required material consumption
    # -------------------------------------------------------------
    # Find a completed order that has at least 2 consumptions
    target_order = None
    target_cons = None
    for o in orders:
        if o["order_status"] == "COMPLETED":
            o_cons = [c for c in consumptions if c["production_order_id"] == o["production_order_id"]]
            if len(o_cons) >= 2:
                target_order = o
                target_cons = o_cons[0]
                break

    if target_order and target_cons:
        # Remove the consumption record
        consumptions.remove(target_cons)
        ground_truth.append({
            "anomaly_id": "ANOMALY-002",
            "anomaly_type": "MISSING_BOM_CONSUMPTION",
            "entity_type": "PRODUCTION_ORDER",
            "entity_id": target_order["production_order_id"],
            "description": f"Completed order {target_order['production_order_id']} is missing mandatory BOM line consumption {target_cons['bom_line_id']}.",
            "expected_validator_rule": "VAL_ORDER_BOM_CONSUMPTION_COMPLETE",
            "injected_details": f"Removed consumption {target_cons['consumption_id']} for BOM line {target_cons['bom_line_id']}.",
        })

    # -------------------------------------------------------------
    # Scenario 3: Corrective action closed without successful verification
    # -------------------------------------------------------------
    # Find an open CAPA (without verifications)
    target_capa = None
    for c in capas:
        c_verifs = [v for v in verifications if v["corrective_action_id"] == c["corrective_action_id"]]
        if not c_verifs:
            target_capa = c
            break

    # If all were verified, take the last CAPA and remove its verifications
    if not target_capa and capas:
        target_capa = capas[-1]
        for v in list(verifications):
            if v["corrective_action_id"] == target_capa["corrective_action_id"]:
                verifications.remove(v)

    if target_capa:
        # Append an illegitimate premature closure StateEvent
        target_capa["corrective_action_status"] = "CLOSED"
        total_events_count += 1
        capa_events = [e for e in events if e["entity_type"] == "CORRECTIVE_ACTION" and e["entity_id"] == target_capa["corrective_action_id"]]
        next_seq = max((e["event_sequence"] for e in capa_events), default=0) + 1

        events.append({
            "event_id": format_event_id(total_events_count),
            "entity_type": "CORRECTIVE_ACTION",
            "entity_id": target_capa["corrective_action_id"],
            "material_lot_id": None,
            "production_order_id": None,
            "inspection_result_id": None,
            "defect_id": None,
            "corrective_action_id": target_capa["corrective_action_id"],
            "event_sequence": next_seq,
            "previous_state": "OPEN",
            "new_state": "CLOSED",
            "event_timestamp": f"{target_capa['due_date']}T12:00:00+00:00",
            "actor_role": "QUALITY_ENGINEER",
            "reason_code": "RC_PREMATURE_CLOSE_ANOMALY",
            "event_notes": "Premature closure injected without verification audit.",
        })

        ground_truth.append({
            "anomaly_id": "ANOMALY-003",
            "anomaly_type": "PREMATURE_CAPA_CLOSURE",
            "entity_type": "CORRECTIVE_ACTION",
            "entity_id": target_capa["corrective_action_id"],
            "description": f"CAPA {target_capa['corrective_action_id']} transitioned to CLOSED without a preceding passed CAPAVerification audit.",
            "expected_validator_rule": "VAL_CAPA_CLOSURE_REQUIRES_VERIFICATION",
            "injected_details": "Appended StateEvent(new_state='CLOSED') directly to unverified CAPA.",
        })

    # -------------------------------------------------------------
    # Scenario 4: Defect quantity exceeds inspected sample quantity
    # -------------------------------------------------------------
    if len(defects) >= 2:
        target_defect_4 = defects[1]
        parent_insp = next((i for i in inspections if i["inspection_result_id"] == target_defect_4["inspection_result_id"]), None)
        if parent_insp:
            original_defect_qty = target_defect_4["defect_quantity"]
            target_defect_4["defect_quantity"] = float(round(parent_insp["inspected_quantity"] + 150.0, 2))

            ground_truth.append({
                "anomaly_id": "ANOMALY-004",
                "anomaly_type": "DEFECT_QUANTITY_EXCEEDS_INSPECTED",
                "entity_type": "DEFECT",
                "entity_id": target_defect_4["defect_id"],
                "description": f"Defect {target_defect_4['defect_id']} has defect_quantity={target_defect_4['defect_quantity']}, which exceeds parent inspected_quantity={parent_insp['inspected_quantity']}.",
                "expected_validator_rule": "VAL_DEFECT_QUANTITY_LE_INSPECTED",
                "injected_details": f"Original defect_qty={original_defect_qty} inflated above inspected_qty={parent_insp['inspected_quantity']}.",
            })

    # -------------------------------------------------------------
    # Scenario 5: Broken traceability chain (cross-order execution mismatch)
    # -------------------------------------------------------------
    if len(defects) >= 3 and len(orders) >= 2:
        target_defect_5 = defects[2]
        orig_order_id = target_defect_5["production_order_id"]
        # Find another order and one of its executions
        other_order = next((o for o in orders if o["production_order_id"] != orig_order_id), None)
        if other_order:
            other_pex = next((p for p in executions if p["production_order_id"] == other_order["production_order_id"]), None)
            if other_pex:
                orig_pex_id = target_defect_5["process_execution_id"]
                target_defect_5["process_execution_id"] = other_pex["process_execution_id"]

                ground_truth.append({
                    "anomaly_id": "ANOMALY-005",
                    "anomaly_type": "BROKEN_TRACEABILITY_CHAIN",
                    "entity_type": "DEFECT",
                    "entity_id": target_defect_5["defect_id"],
                    "description": f"Defect {target_defect_5['defect_id']} references ProcessExecution {other_pex['process_execution_id']}, which belongs to ProductionOrder {other_order['production_order_id']}, conflicting with Defect's ProductionOrder {orig_order_id}.",
                    "expected_validator_rule": "VAL_DEFECT_PROCESS_EXECUTION_ORDER_MATCH",
                    "injected_details": f"Replaced execution {orig_pex_id} with cross-order execution {other_pex['process_execution_id']}.",
                })

    return modified_dataset, ground_truth
