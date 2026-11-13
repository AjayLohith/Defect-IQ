"""StateEvent and outcome generation skeleton for Phase 3."""
from datetime import datetime
from typing import Dict, List, Any
from generator.src.ids import format_event_id


def generate_baseline_events(transactions: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generates append-only StateEvent records for baseline transactions with immutable event_sequence."""
    state_events: List[Dict[str, Any]] = []
    event_seq = 1

    # 1. Events for Material Lots
    for lot in transactions["material_lots"]:
        # Event 1: RECEIVED
        eid = format_event_id(event_seq)
        state_events.append({
            "event_id": eid,
            "entity_type": "MATERIAL_LOT",
            "entity_id": lot["material_lot_id"],
            "material_lot_id": lot["material_lot_id"],
            "production_order_id": None,
            "inspection_result_id": None,
            "defect_id": None,
            "corrective_action_id": None,
            "event_sequence": 1,
            "previous_state": None,
            "new_state": "RECEIVED",
            "event_timestamp": f"{lot['received_date']}T08:00:00+00:00",
            "actor_role": "PLANT_OPERATOR",
            "reason_code": "RC_INWARD_RECEIPT",
            "event_notes": "Initial material lot delivery accepted.",
        })
        event_seq += 1

        # Event 2: RELEASED
        eid = format_event_id(event_seq)
        state_events.append({
            "event_id": eid,
            "entity_type": "MATERIAL_LOT",
            "entity_id": lot["material_lot_id"],
            "material_lot_id": lot["material_lot_id"],
            "production_order_id": None,
            "inspection_result_id": None,
            "defect_id": None,
            "corrective_action_id": None,
            "event_sequence": 2,
            "previous_state": "RECEIVED",
            "new_state": "RELEASED",
            "event_timestamp": f"{lot['received_date']}T12:00:00+00:00",
            "actor_role": "QUALITY_ENGINEER",
            "reason_code": "RC_QUALITY_CLEARANCE",
            "event_notes": "Incoming quality inspection passed. Lot released for production.",
        })
        event_seq += 1

        # Event 3: If consumed or partially consumed
        if lot["lot_status"] in ("PARTIALLY_CONSUMED", "CONSUMED"):
            eid = format_event_id(event_seq)
            state_events.append({
                "event_id": eid,
                "entity_type": "MATERIAL_LOT",
                "entity_id": lot["material_lot_id"],
                "material_lot_id": lot["material_lot_id"],
                "production_order_id": None,
                "inspection_result_id": None,
                "defect_id": None,
                "corrective_action_id": None,
                "event_sequence": 3,
                "previous_state": "RELEASED",
                "new_state": lot["lot_status"],
                "event_timestamp": f"{lot['received_date']}T16:00:00+00:00",
                "actor_role": "PLANT_OPERATOR",
                "reason_code": "RC_PRODUCTION_ISSUE",
                "event_notes": f"Material allocated to production line. Balance: {lot['available_quantity']} {lot['uom']}.",
            })
            event_seq += 1

    # 2. Events for Production Orders
    for order in transactions["production_orders"]:
        # Event 1: PLANNED
        eid = format_event_id(event_seq)
        state_events.append({
            "event_id": eid,
            "entity_type": "PRODUCTION_ORDER",
            "entity_id": order["production_order_id"],
            "material_lot_id": None,
            "production_order_id": order["production_order_id"],
            "inspection_result_id": None,
            "defect_id": None,
            "corrective_action_id": None,
            "event_sequence": 1,
            "previous_state": None,
            "new_state": "PLANNED",
            "event_timestamp": f"{order['planned_start_date']}T06:00:00+00:00",
            "actor_role": "PRODUCTION_PLANNER",
            "reason_code": "RC_ORDER_SCHEDULED",
            "event_notes": f"Order scheduled for {order['planned_quantity']} units.",
        })
        event_seq += 1

        seq_counter = 2
        if order["actual_start_date"]:
            # Event 2: RELEASED
            eid = format_event_id(event_seq)
            state_events.append({
                "event_id": eid,
                "entity_type": "PRODUCTION_ORDER",
                "entity_id": order["production_order_id"],
                "material_lot_id": None,
                "production_order_id": order["production_order_id"],
                "inspection_result_id": None,
                "defect_id": None,
                "corrective_action_id": None,
                "event_sequence": seq_counter,
                "previous_state": "PLANNED",
                "new_state": "RELEASED",
                "event_timestamp": f"{order['actual_start_date']}T07:30:00+00:00",
                "actor_role": "PRODUCTION_PLANNER",
                "reason_code": "RC_MATERIALS_ALLOCATED",
                "event_notes": "BOM components staged and verified.",
            })
            event_seq += 1
            seq_counter += 1

            # Event 3: IN_PROGRESS
            eid = format_event_id(event_seq)
            state_events.append({
                "event_id": eid,
                "entity_type": "PRODUCTION_ORDER",
                "entity_id": order["production_order_id"],
                "material_lot_id": None,
                "production_order_id": order["production_order_id"],
                "inspection_result_id": None,
                "defect_id": None,
                "corrective_action_id": None,
                "event_sequence": seq_counter,
                "previous_state": "RELEASED",
                "new_state": "IN_PROGRESS",
                "event_timestamp": f"{order['actual_start_date']}T08:00:00+00:00",
                "actor_role": "PLANT_OPERATOR",
                "reason_code": "RC_EXECUTION_COMMENCED",
                "event_notes": "Primary routing sequence initiated.",
            })
            event_seq += 1
            seq_counter += 1

            # Terminal Event if COMPLETED or SCRAPPED
            if order["order_status"] in ("COMPLETED", "SCRAPPED") and order["actual_end_date"]:
                eid = format_event_id(event_seq)
                state_events.append({
                    "event_id": eid,
                    "entity_type": "PRODUCTION_ORDER",
                    "entity_id": order["production_order_id"],
                    "material_lot_id": None,
                    "production_order_id": order["production_order_id"],
                    "inspection_result_id": None,
                    "defect_id": None,
                    "corrective_action_id": None,
                    "event_sequence": seq_counter,
                    "previous_state": "IN_PROGRESS",
                    "new_state": order["order_status"],
                    "event_timestamp": f"{order['actual_end_date']}T17:00:00+00:00",
                    "actor_role": "PLANT_OPERATOR",
                    "reason_code": "RC_EXECUTION_TERMINATED",
                    "event_notes": f"Order disposition: {order['order_status']}. Accepted: {order['accepted_quantity']}.",
                })
                event_seq += 1

    return state_events
