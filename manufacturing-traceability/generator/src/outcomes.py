"""Inspection outcomes, defects, containment, CAPAs, and append-only StateEvents."""
import random
from datetime import timedelta
from typing import Dict, List, Any
from generator.src.config import BASE_EPOCH, derive_subseed
from generator.src.ids import (
    format_defect_id,
    format_containment_id,
    format_capa_id,
    format_verification_id,
    format_event_id,
)

DEFECT_TAXONOMY = [
    ("ERR-DIM-001", "DIMENSIONAL", "Shaft Diameter Out of Tolerance", "MACHINE"),
    ("ERR-SURF-002", "SURFACE_FINISH", "Excessive Surface Roughness Ra > 1.6", "MACHINE"),
    ("ERR-ELEC-003", "ELECTRICAL", "Coil Insulation Breakdown Resistance < 10M Ohm", "MATERIAL"),
    ("ERR-CONT-004", "CONTAMINATION", "Particulate Contamination on Sealing Surface", "ENVIRONMENT"),
    ("ERR-ALGN-005", "ASSEMBLY_ALIGNMENT", "Misaligned Pin Connector Insertion", "OPERATOR"),
    ("ERR-WELD-006", "DIMENSIONAL", "Laser Weld Seam Penetration Depth Insufficient", "MACHINE"),
]

ROOT_CAUSES = [
    ("SUPPLIER_QUALITY", "Raw material hardness exceeded ASTM specification bounds.", "Zero defect recurrence in supplier inwarding for 60 days"),
    ("TOOLING_WEAR", "End mill insert micro-fracture causing dimensional drift.", "Insert replacement schedule updated to 2500 cycles with automated tool wear sensing"),
    ("CALIBRATION_DRIFT", "Pyrometer sensor drift caused temperature drop during welding.", "Bi-weekly calibration routine instituted with secondary reference probe"),
    ("SETUP_ERROR", "Fixture clamping pressure set 15% below required torque.", "Digital torque wrench integration with interlock quality gate"),
    ("PROCEDURAL_OMISSION", "Work instruction step 4 degreasing protocol omitted by operator.", "Visual SOP sign-off incorporated into operator terminal routing"),
]


def generate_outcomes_and_defects(
    master_data: Dict[str, Any],
    transactions: Dict[str, Any],
    master_seed: int,
) -> Dict[str, Any]:
    """Generates Defects, ContainmentActions, CorrectiveActions, CAPAVerifications, and StateEvents."""
    prng = random.Random(derive_subseed(master_seed, "outcomes"))

    material_lots = transactions["material_lots"]
    production_orders = transactions["production_orders"]
    consumptions = transactions["material_consumptions"]
    process_executions = transactions["process_executions"]
    inspection_results = transactions["inspection_results"]

    # Index material consumptions by production_order_id
    consumptions_by_order: Dict[str, List[Dict[str, Any]]] = {}
    for c in consumptions:
        consumptions_by_order.setdefault(c["production_order_id"], []).append(c)

    # Index executions by pex_id
    pex_by_id: Dict[str, Dict[str, Any]] = {p["process_execution_id"]: p for p in process_executions}
    lots_by_id: Dict[str, Dict[str, Any]] = {l["material_lot_id"]: l for l in material_lots}

    defects: List[Dict[str, Any]] = []
    containment_actions: List[Dict[str, Any]] = []
    corrective_actions: List[Dict[str, Any]] = []
    capa_verifications: List[Dict[str, Any]] = []
    state_events: List[Dict[str, Any]] = []

    defect_seq = 1
    cnt_seq = 1
    capa_seq = 1
    verif_seq = 1
    event_seq = 1

    # 1. StateEvents for MaterialLots
    for lot in material_lots:
        # Event 1: RECEIVED
        state_events.append({
            "event_id": format_event_id(event_seq),
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
        state_events.append({
            "event_id": format_event_id(event_seq),
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

        if lot["lot_status"] in ("PARTIALLY_CONSUMED", "CONSUMED"):
            state_events.append({
                "event_id": format_event_id(event_seq),
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

    # 2. StateEvents for ProductionOrders
    for order in production_orders:
        state_events.append({
            "event_id": format_event_id(event_seq),
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
            state_events.append({
                "event_id": format_event_id(event_seq),
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

            state_events.append({
                "event_id": format_event_id(event_seq),
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

            if order["order_status"] in ("COMPLETED", "SCRAPPED") and order["actual_end_date"]:
                state_events.append({
                    "event_id": format_event_id(event_seq),
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

    # 3. Generate Defects from Inspections with Rejected Units
    for insp in inspection_results:
        # Event for InspectionResult
        state_events.append({
            "event_id": format_event_id(event_seq),
            "entity_type": "INSPECTION_RESULT",
            "entity_id": insp["inspection_result_id"],
            "material_lot_id": None,
            "production_order_id": None,
            "inspection_result_id": insp["inspection_result_id"],
            "defect_id": None,
            "corrective_action_id": None,
            "event_sequence": 1,
            "previous_state": "PENDING",
            "new_state": "COMPLETED",
            "event_timestamp": insp["inspected_at"],
            "actor_role": "QUALITY_ENGINEER",
            "reason_code": "RC_INSPECTION_FINALIZED",
            "event_notes": f"Disposition: {insp['disposition']}. Defect rate: {insp['defect_rate']}.",
        })
        event_seq += 1

        if insp["rejected_quantity"] > 0:
            order_id = insp["production_order_id"]
            pex = pex_by_id[insp["process_execution_id"]]
            order_cons = consumptions_by_order.get(order_id, [])

            # Resolve material lot and supplier
            if order_cons:
                selected_cons = order_cons[defect_seq % len(order_cons)]
                mat_lot_id = selected_cons["material_lot_id"]
                lot_obj = lots_by_id.get(mat_lot_id)
                supp_id = lot_obj["supplier_id"] if lot_obj else None
            else:
                mat_lot_id = None
                supp_id = None

            defect_id = format_defect_id(2026, defect_seq)
            tax_item = DEFECT_TAXONOMY[(defect_seq - 1) % len(DEFECT_TAXONOMY)]

            # Severity: 15% CRITICAL, 35% MAJOR, 50% MINOR
            sev_roll = defect_seq % 100
            if sev_roll < 15:
                severity = "CRITICAL"
            elif sev_roll < 50:
                severity = "MAJOR"
            else:
                severity = "MINOR"

            defect = {
                "defect_id": defect_id,
                "inspection_result_id": insp["inspection_result_id"],
                "production_order_id": order_id,
                "process_execution_id": pex["process_execution_id"],
                "machine_id": pex["machine_id"],
                "material_lot_id": mat_lot_id,
                "reported_material_lot_id": mat_lot_id if mat_lot_id else "LOT-UNKNOWN",
                "supplier_id": supp_id,
                "defect_code": tax_item[0],
                "defect_category": tax_item[1],
                "severity": severity,
                "defect_quantity": min(insp["rejected_quantity"], insp["inspected_quantity"]),
                "suspected_source": tax_item[3],
                "detected_at": insp["inspected_at"],
                "defect_status": "OPEN",
            }
            defects.append(defect)

            # Defect Event 1: OPEN
            state_events.append({
                "event_id": format_event_id(event_seq),
                "entity_type": "DEFECT",
                "entity_id": defect_id,
                "material_lot_id": None,
                "production_order_id": None,
                "inspection_result_id": None,
                "defect_id": defect_id,
                "corrective_action_id": None,
                "event_sequence": 1,
                "previous_state": None,
                "new_state": "OPEN",
                "event_timestamp": defect["detected_at"],
                "actor_role": "QUALITY_ENGINEER",
                "reason_code": "RC_DEFECT_DISCOVERED",
                "event_notes": f"Defect {tax_item[0]} logged with severity {severity}.",
            })
            event_seq += 1

            # 4. Containment Actions for Critical and Major Defects
            if severity in ("CRITICAL", "MAJOR"):
                cnt_id = format_containment_id(2026, cnt_seq)
                cnt_dt = datetime_from_iso(defect["detected_at"]) + timedelta(minutes=15)
                action_type = "QUARANTINE_LOT" if defect["suspected_source"] == "MATERIAL" else "STOP_LINE" if severity == "CRITICAL" else "REWORK_WIP"

                cnt = {
                    "containment_action_id": cnt_id,
                    "defect_id": defect_id,
                    "action_type": action_type,
                    "owner_role": "QUALITY_ENGINEER",
                    "action_timestamp": cnt_dt.isoformat(),
                    "affected_quantity": defect["defect_quantity"],
                    "containment_status": "ACTIVE",
                    "notes": f"Immediate {action_type} executed to isolate non-conforming WIP.",
                }
                containment_actions.append(cnt)
                cnt_seq += 1

                # Defect Event 2: CONTAINED
                state_events.append({
                    "event_id": format_event_id(event_seq),
                    "entity_type": "DEFECT",
                    "entity_id": defect_id,
                    "material_lot_id": None,
                    "production_order_id": None,
                    "inspection_result_id": None,
                    "defect_id": defect_id,
                    "corrective_action_id": None,
                    "event_sequence": 2,
                    "previous_state": "OPEN",
                    "new_state": "CONTAINED",
                    "event_timestamp": cnt["action_timestamp"],
                    "actor_role": "QUALITY_ENGINEER",
                    "reason_code": "RC_CONTAINMENT_SET",
                    "event_notes": f"Active containment {action_type} confirmed.",
                })
                event_seq += 1
                defect["defect_status"] = "CONTAINED"

                # 5. Corrective Action (CAPA) for every Critical defect and alternate Major
                if severity == "CRITICAL" or (severity == "MAJOR" and defect_seq % 2 == 0):
                    capa_id = format_capa_id(2026, capa_seq)
                    root_cause = ROOT_CAUSES[(capa_seq - 1) % len(ROOT_CAUSES)]
                    capa_open_dt = datetime_from_iso(cnt["action_timestamp"]) + timedelta(hours=2)
                    due_date = (datetime_from_iso(cnt["action_timestamp"]) + timedelta(days=30)).date()

                    capa = {
                        "corrective_action_id": capa_id,
                        "defect_id": defect_id,
                        "root_cause_category": root_cause[0],
                        "root_cause_description": root_cause[1],
                        "owner_role": "QUALITY_ENGINEER",
                        "due_date": due_date.isoformat(),
                        "implementation_date": (due_date + timedelta(days=-5)).isoformat(),
                        "corrective_action_status": "OPEN",
                        "effectiveness_target": root_cause[2],
                    }
                    corrective_actions.append(capa)

                    # CAPA Event 1: OPEN
                    state_events.append({
                        "event_id": format_event_id(event_seq),
                        "entity_type": "CORRECTIVE_ACTION",
                        "entity_id": capa_id,
                        "material_lot_id": None,
                        "production_order_id": None,
                        "inspection_result_id": None,
                        "defect_id": None,
                        "corrective_action_id": capa_id,
                        "event_sequence": 1,
                        "previous_state": None,
                        "new_state": "OPEN",
                        "event_timestamp": capa_open_dt.isoformat(),
                        "actor_role": "QUALITY_ENGINEER",
                        "reason_code": "RC_CAPA_INITIATED",
                        "event_notes": f"Formal CAPA initiated for {defect_id}.",
                    })
                    event_seq += 1

                    # Defect Event 3: CAPA_IN_PROGRESS
                    state_events.append({
                        "event_id": format_event_id(event_seq),
                        "entity_type": "DEFECT",
                        "entity_id": defect_id,
                        "material_lot_id": None,
                        "production_order_id": None,
                        "inspection_result_id": None,
                        "defect_id": defect_id,
                        "corrective_action_id": None,
                        "event_sequence": 3,
                        "previous_state": "CONTAINED",
                        "new_state": "CAPA_IN_PROGRESS",
                        "event_timestamp": capa_open_dt.isoformat(),
                        "actor_role": "QUALITY_ENGINEER",
                        "reason_code": "RC_CAPA_ASSIGNED",
                        "event_notes": f"Assigned to {capa_id}.",
                    })
                    event_seq += 1
                    defect["defect_status"] = "CAPA_IN_PROGRESS"

                    # 6. CAPA progression: IMPLEMENTED -> VERIFICATION_PENDING -> VERIFIED -> CLOSED
                    # Progress completed CAPAs (e.g. 60% of them)
                    if capa_seq % 5 != 0:
                        impl_dt = datetime_from_iso(capa_open_dt.isoformat()) + timedelta(days=10)
                        capa["corrective_action_status"] = "IMPLEMENTED"

                        # CAPA Event 2: IMPLEMENTED
                        state_events.append({
                            "event_id": format_event_id(event_seq),
                            "entity_type": "CORRECTIVE_ACTION",
                            "entity_id": capa_id,
                            "material_lot_id": None,
                            "production_order_id": None,
                            "inspection_result_id": None,
                            "defect_id": None,
                            "corrective_action_id": capa_id,
                            "event_sequence": 2,
                            "previous_state": "OPEN",
                            "new_state": "IMPLEMENTED",
                            "event_timestamp": impl_dt.isoformat(),
                            "actor_role": "QUALITY_ENGINEER",
                            "reason_code": "RC_COUNTERMEASURE_DEPLOYED",
                            "event_notes": "Preventative tooling update and sensor interlocks deployed.",
                        })
                        event_seq += 1

                        verif_id = format_verification_id(2026, verif_seq)
                        verif_date = (datetime_from_iso(impl_dt.isoformat()) + timedelta(days=7)).date()
                        verif = {
                            "verification_id": verif_id,
                            "corrective_action_id": capa_id,
                            "verification_date": verif_date.isoformat(),
                            "verification_method": "AUDIT_CHECK" if verif_seq % 2 == 0 else "SPC_MONITORING",
                            "verification_result": "PASSED",
                            "verified_by_role": "QUALITY_ENGINEER",
                            "evidence_reference": f"DOC-AUDIT-2026-{verif_seq:04d}",
                        }
                        capa_verifications.append(verif)
                        verif_seq += 1

                        # CAPA Event 3: VERIFIED
                        verif_dt = datetime_from_iso(f"{verif_date.isoformat()}T14:00:00+00:00")
                        state_events.append({
                            "event_id": format_event_id(event_seq),
                            "entity_type": "CORRECTIVE_ACTION",
                            "entity_id": capa_id,
                            "material_lot_id": None,
                            "production_order_id": None,
                            "inspection_result_id": None,
                            "defect_id": None,
                            "corrective_action_id": capa_id,
                            "event_sequence": 3,
                            "previous_state": "IMPLEMENTED",
                            "new_state": "VERIFIED",
                            "event_timestamp": verif_dt.isoformat(),
                            "actor_role": "QUALITY_ENGINEER",
                            "reason_code": "RC_EFFECTIVENESS_VERIFIED",
                            "event_notes": f"Verification {verif_id} passed: {verif['evidence_reference']}.",
                        })
                        event_seq += 1

                        # CAPA Event 4: CLOSED
                        close_dt = verif_dt + timedelta(hours=4)
                        state_events.append({
                            "event_id": format_event_id(event_seq),
                            "entity_type": "CORRECTIVE_ACTION",
                            "entity_id": capa_id,
                            "material_lot_id": None,
                            "production_order_id": None,
                            "inspection_result_id": None,
                            "defect_id": None,
                            "corrective_action_id": capa_id,
                            "event_sequence": 4,
                            "previous_state": "VERIFIED",
                            "new_state": "CLOSED",
                            "event_timestamp": close_dt.isoformat(),
                            "actor_role": "QUALITY_ENGINEER",
                            "reason_code": "RC_FORMAL_CLOSURE",
                            "event_notes": "CAPA signed off and archived.",
                        })
                        event_seq += 1
                        capa["corrective_action_status"] = "CLOSED"

                        # Defect Event 4: VERIFIED
                        state_events.append({
                            "event_id": format_event_id(event_seq),
                            "entity_type": "DEFECT",
                            "entity_id": defect_id,
                            "material_lot_id": None,
                            "production_order_id": None,
                            "inspection_result_id": None,
                            "defect_id": defect_id,
                            "corrective_action_id": None,
                            "event_sequence": 4,
                            "previous_state": "CAPA_IN_PROGRESS",
                            "new_state": "VERIFIED",
                            "event_timestamp": verif_dt.isoformat(),
                            "actor_role": "QUALITY_ENGINEER",
                            "reason_code": "RC_DEFECT_RESOLVED",
                            "event_notes": f"Verified by CAPA {capa_id}.",
                        })
                        event_seq += 1

                        # Defect Event 5: CLOSED
                        state_events.append({
                            "event_id": format_event_id(event_seq),
                            "entity_type": "DEFECT",
                            "entity_id": defect_id,
                            "material_lot_id": None,
                            "production_order_id": None,
                            "inspection_result_id": None,
                            "defect_id": defect_id,
                            "corrective_action_id": None,
                            "event_sequence": 5,
                            "previous_state": "VERIFIED",
                            "new_state": "CLOSED",
                            "event_timestamp": close_dt.isoformat(),
                            "actor_role": "QUALITY_ENGINEER",
                            "reason_code": "RC_DEFECT_CLOSED",
                            "event_notes": "Defect lifecycle completed.",
                        })
                        event_seq += 1
                        defect["defect_status"] = "CLOSED"

                    capa_seq += 1

            defect_seq += 1

    return {
        "defects": defects,
        "containment_actions": containment_actions,
        "corrective_actions": corrective_actions,
        "capa_verifications": capa_verifications,
        "state_events": state_events,
    }


def datetime_from_iso(dt_str: str):
    from datetime import datetime
    return datetime.fromisoformat(dt_str)
