"""Transactional data generation: Material Lots, Orders, Consumptions, Executions, Inspections."""
import random
from datetime import timedelta
from typing import Dict, List, Any
from generator.src.config import DatasetProfile, BASE_EPOCH, derive_subseed
from generator.src.ids import (
    format_lot_id,
    format_order_id,
    format_production_lot_code,
    format_consumption_id,
    format_process_execution_id,
    format_inspection_id,
)


def generate_transactions(master_data: Dict[str, Any], profile: DatasetProfile, master_seed: int) -> Dict[str, Any]:
    """Generates all transactional entities with deterministic arithmetic reconciliation."""
    prng = random.Random(derive_subseed(master_seed, "transactions"))

    fg_products = master_data["fg_products"]
    rm_products = master_data["rm_products"]
    suppliers = master_data["suppliers"]
    boms = master_data["boms"]
    bom_lines = master_data["bom_lines"]
    machines = master_data["machines"]
    process_steps = master_data["process_steps"]
    inspection_plans = master_data["inspection_plans"]

    # Pre-index BOM lines by BOM ID and product ID
    boms_by_product: Dict[str, Dict[str, Any]] = {b["product_id"]: b for b in boms}
    bom_lines_by_bom: Dict[str, List[Dict[str, Any]]] = {}
    for bl in bom_lines:
        bom_lines_by_bom.setdefault(bl["bom_id"], []).append(bl)

    # Compatible machines by machine_type
    machines_by_type: Dict[str, List[Dict[str, Any]]] = {}
    for m in machines:
        machines_by_type.setdefault(m["machine_type"], []).append(m)

    # Inspection plan lookup by (product_id, process_step_id)
    plan_lookup: Dict[tuple, Dict[str, Any]] = {
        (p["product_id"], p["process_step_id"]): p for p in inspection_plans
    }

    # 1. Generate Material Lots
    material_lots: List[Dict[str, Any]] = []
    lots_by_rm: Dict[str, List[Dict[str, Any]]] = {}

    for i in range(1, profile.material_lot_count + 1):
        supp_idx = ((i - 1) % len(suppliers)) + 1
        supplier = suppliers[supp_idx - 1]
        rm = rm_products[(i - 1) % len(rm_products)]

        lot_id = format_lot_id(supp_idx, 2026, i)
        recv_date = (BASE_EPOCH + timedelta(days=-120 + (i % 60))).date()
        expiry_date = (BASE_EPOCH + timedelta(days=240 + (i % 120))).date()

        base_qty = float(round(10000.0 + (i % 10) * 1000.0, 4))
        # Initial lot balances (will be depleted by consumptions)
        lot = {
            "material_lot_id": lot_id,
            "supplier_id": supplier["supplier_id"],
            "material_product_id": rm["product_id"],
            "supplier_batch_code": f"BATCH-2026-SUP{supp_idx:04d}-{i:05d}",
            "received_date": recv_date.isoformat(),
            "expiry_date": expiry_date.isoformat(),
            "received_quantity": base_qty,
            "available_quantity": base_qty,
            "consumed_quantity": 0.0,
            "rejected_quantity": 0.0,
            "quarantined_quantity": 0.0,
            "uom": rm["base_uom"],
            "lot_status": "RELEASED",
            "incoming_quality_score": float(round(92.0 + (i % 8) * 1.0, 2)),
        }
        material_lots.append(lot)
        lots_by_rm.setdefault(rm["product_id"], []).append(lot)

    # 2. Generate Production Orders
    production_orders: List[Dict[str, Any]] = []
    material_consumptions: List[Dict[str, Any]] = []
    process_executions: List[Dict[str, Any]] = []
    inspection_results: List[Dict[str, Any]] = []

    cons_seq = 1
    pex_seq = 1
    insp_target = profile.inspection_result_count

    # Plan orders over a deterministic 180-day operational timeline
    for i in range(1, profile.production_order_count + 1):
        order_id = format_order_id(2026, i)
        fg = fg_products[(i - 1) % len(fg_products)]
        bom = boms_by_product[fg["product_id"]]
        order_bom_lines = bom_lines_by_bom[bom["bom_id"]]

        lot_code = format_production_lot_code(2026, i)
        order_day_offset = (i * 180) // profile.production_order_count
        planned_start = (BASE_EPOCH + timedelta(days=order_day_offset)).date()
        planned_end = (BASE_EPOCH + timedelta(days=order_day_offset + 3)).date()

        planned_qty = float(round(50.0 + (i % 6) * 25.0, 2))

        # Order status: 80% COMPLETED, 10% IN_PROGRESS, 5% ON_HOLD, 3% REWORK, 2% SCRAPPED
        status_roll = i % 100
        if status_roll < 80:
            order_status = "COMPLETED"
        elif status_roll < 90:
            order_status = "IN_PROGRESS"
        elif status_roll < 95:
            order_status = "ON_HOLD"
        elif status_roll < 98:
            order_status = "REWORK"
        else:
            order_status = "SCRAPPED"

        is_finished = order_status in ("COMPLETED", "SCRAPPED")
        actual_start = planned_start if is_finished or order_status in ("IN_PROGRESS", "ON_HOLD", "REWORK") else None
        actual_end = planned_end if is_finished else None

        # Order quantity partitions
        if order_status == "COMPLETED":
            completed_qty = planned_qty
            # Realistic yield: ~96% accepted, small rework/scrap/quarantine
            scrap_qty = float(round(1.0 if (i % 15 == 0) else 0.0, 2))
            rework_qty = float(round(2.0 if (i % 10 == 0) else 0.0, 2))
            quar_qty = float(round(1.0 if (i % 25 == 0) else 0.0, 2))
            accepted_qty = float(round(completed_qty - (scrap_qty + rework_qty + quar_qty), 2))
        elif order_status == "SCRAPPED":
            completed_qty = planned_qty
            scrap_qty = planned_qty
            accepted_qty = 0.0
            rework_qty = 0.0
            quar_qty = 0.0
        else:
            completed_qty = float(round(planned_qty * 0.4, 2))
            accepted_qty = completed_qty
            scrap_qty = 0.0
            rework_qty = 0.0
            quar_qty = 0.0

        order = {
            "production_order_id": order_id,
            "product_id": fg["product_id"],
            "planned_quantity": planned_qty,
            "completed_quantity": completed_qty,
            "accepted_quantity": accepted_qty,
            "rework_quantity": rework_qty,
            "scrap_quantity": scrap_qty,
            "quarantined_quantity": quar_qty,
            "order_status": order_status,
            "planned_start_date": planned_start.isoformat(),
            "planned_end_date": planned_end.isoformat(),
            "actual_start_date": actual_start.isoformat() if actual_start else None,
            "actual_end_date": actual_end.isoformat() if actual_end else None,
            "production_lot_code": lot_code,
        }
        production_orders.append(order)

        # 3. Material Consumptions for the order (if started)
        if actual_start:
            order_start_dt = BASE_EPOCH + timedelta(days=order_day_offset, hours=8)
            for bl in order_bom_lines:
                req_rm = bl["material_product_id"]
                available_lots = lots_by_rm.get(req_rm, [])
                if not available_lots:
                    continue

                # Select a lot with available balance for this raw material
                eligible_lots = [l for l in available_lots if l["available_quantity"] > 0]
                if not eligible_lots:
                    continue
                selected_lot = eligible_lots[(i + cons_seq) % len(eligible_lots)]
                needed_qty = float(round(planned_qty * bl["quantity_per_unit"] * (1.0 + bl["scrap_factor"]), 4))

                # Strictly deduct only up to available balance
                consume_qty = min(needed_qty, selected_lot["available_quantity"])
                if consume_qty <= 0:
                    continue

                selected_lot["available_quantity"] = float(round(selected_lot["available_quantity"] - consume_qty, 4))
                selected_lot["consumed_quantity"] = float(round(selected_lot["consumed_quantity"] + consume_qty, 4))
                if selected_lot["available_quantity"] <= 0:
                    selected_lot["lot_status"] = "CONSUMED"
                else:
                    selected_lot["lot_status"] = "PARTIALLY_CONSUMED"

                cid = format_consumption_id(cons_seq)
                cons = {
                    "consumption_id": cid,
                    "production_order_id": order_id,
                    "material_lot_id": selected_lot["material_lot_id"],
                    "bom_line_id": bl["bom_line_id"],
                    "consumed_quantity": consume_qty,
                    "uom": bl["uom"],
                    "consumed_at": (order_start_dt + timedelta(minutes=cons_seq % 60)).isoformat(),
                    "consumption_status": "COMMITTED",
                }
                material_consumptions.append(cons)
                cons_seq += 1

        # 4. Process Executions for the order (if started)
        order_executions: List[Dict[str, Any]] = []
        if actual_start:
            current_dt = BASE_EPOCH + timedelta(days=order_day_offset, hours=9)
            current_input = planned_qty

            for step in process_steps:
                compatible_m = machines_by_type.get(step["allowed_machine_type"], machines)
                selected_m = compatible_m[(i + step["step_sequence"]) % len(compatible_m)]

                start_at = current_dt
                duration_secs = step["standard_cycle_time_seconds"] * int(max(1.0, current_input // 10))
                end_at = start_at + timedelta(seconds=duration_secs)
                current_dt = end_at + timedelta(minutes=15)

                # Process partition reconciliation
                step_scrap = float(round(1.0 if (step["is_quality_gate"] and i % 20 == 0) else 0.0, 2))
                step_rework = float(round(1.0 if (step["is_quality_gate"] and i % 14 == 0) else 0.0, 2))
                step_quar = 0.0
                step_output = float(round(current_input - (step_scrap + step_rework + step_quar), 2))

                # Deterministic drift calculation: machine risk + time window
                is_drift = (selected_m["maintenance_risk_score"] > 50.0) and ((order_day_offset % 30) < 5)

                pid = format_process_execution_id(pex_seq)
                pex = {
                    "process_execution_id": pid,
                    "production_order_id": order_id,
                    "process_step_id": step["process_step_id"],
                    "machine_id": selected_m["machine_id"],
                    "execution_start_at": start_at.isoformat(),
                    "execution_end_at": end_at.isoformat(),
                    "input_quantity": current_input,
                    "output_quantity": step_output,
                    "rework_quantity": step_rework,
                    "scrap_quantity": step_scrap,
                    "quarantined_quantity": step_quar,
                    "execution_status": "COMPLETED",
                    "drift_indicator": is_drift,
                    "process_measurement": float(round(25.0 + (pex_seq % 50) * 0.15 + (2.5 if is_drift else 0.0), 3)),
                }
                process_executions.append(pex)
                order_executions.append(pex)
                pex_seq += 1

                current_input = step_output

        # 5. Inspection Results for quality gates
        if actual_start and order_executions:
            insp_seq = 1
            for pex in order_executions:
                step_id = pex["process_step_id"]
                plan = plan_lookup.get((fg["product_id"], step_id))
                if not plan:
                    continue

                insp_id = format_inspection_id(2026, i, insp_seq)
                insp_dt = datetime_from_iso(pex["execution_end_at"]) + timedelta(minutes=10)

                # Sample size: ANSI Z1.4 sampling or fixed sample
                sample_qty = float(min(pex["output_quantity"], 20.0 if pex["output_quantity"] >= 20.0 else pex["output_quantity"]))
                if sample_qty <= 0:
                    sample_qty = 5.0

                # Inspection partition reconciliation:
                # inspected = accepted + rejected
                # rejected = reworked + scrapped + quarantined
                if pex["drift_indicator"] or (i % 12 == 0):
                    # Higher defect rate during drift
                    rej_scrapped = float(round(1.0, 2))
                    rej_reworked = float(round(1.0 if (i % 6 == 0) else 0.0, 2))
                    rej_quarantined = float(round(1.0 if (i % 18 == 0) else 0.0, 2))
                    rejected_qty = float(round(rej_scrapped + rej_reworked + rej_quarantined, 2))
                    accepted_qty = float(round(sample_qty - rejected_qty, 2))
                    if accepted_qty < 0:
                        accepted_qty = 0.0
                        rejected_qty = sample_qty
                        rej_scrapped = sample_qty
                        rej_reworked = 0.0
                        rej_quarantined = 0.0
                    disposition = "REJECTED" if rejected_qty / sample_qty > plan["acceptance_limit"] else "CONDITIONAL_ACCEPTANCE"
                else:
                    rejected_qty = 0.0
                    rej_scrapped = 0.0
                    rej_reworked = 0.0
                    rej_quarantined = 0.0
                    accepted_qty = sample_qty
                    disposition = "ACCEPTED"

                defect_rate = float(round(rejected_qty / sample_qty, 4))

                insp = {
                    "inspection_result_id": insp_id,
                    "inspection_plan_id": plan["inspection_plan_id"],
                    "production_order_id": order_id,
                    "process_execution_id": pex["process_execution_id"],
                    "inspected_at": insp_dt.isoformat(),
                    "inspected_quantity": sample_qty,
                    "accepted_quantity": accepted_qty,
                    "rejected_quantity": rejected_qty,
                    "reworked_quantity": rej_reworked,
                    "scrapped_quantity": rej_scrapped,
                    "quarantined_quantity": rej_quarantined,
                    "inspection_status": "COMPLETED",
                    "disposition": disposition,
                    "defect_rate": defect_rate,
                }
                inspection_results.append(insp)
                insp_seq += 1

    return {
        "material_lots": material_lots,
        "production_orders": production_orders,
        "material_consumptions": material_consumptions,
        "process_executions": process_executions,
        "inspection_results": inspection_results,
    }


def datetime_from_iso(dt_str: str):
    from datetime import datetime
    return datetime.fromisoformat(dt_str)
