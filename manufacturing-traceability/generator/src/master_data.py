"""Master data generation: Products, Suppliers, BOMs, Machines, Steps, Plans."""
import random
from datetime import timedelta
from typing import Dict, List, Any
from generator.src.config import DatasetProfile, BASE_EPOCH, derive_subseed
from generator.src.ids import (
    format_sku_id,
    format_supplier_id,
    format_bom_id,
    format_bom_line_id,
    format_machine_id,
    format_process_step_id,
    format_inspection_plan_id,
)

COUNTRY_CODES = ["US", "DE", "JP", "KR", "MX", "TW", "CA", "GB", "CH", "FR"]

MACHINE_DEFINITIONS = [
    ("CNC_MILL", "High-Precision 5-Axis CNC Mill"),
    ("INJECTION_MOLD", "Hydraulic Thermoplastic Molding Press"),
    ("SMT_PICK_PLACE", "High-Speed SMT Placement System"),
    ("LASER_WELDER", "Automated Fiber Laser Welder"),
    ("OPTICAL_INSPECTOR", "Automated 3D Optical Inspection Station"),
]

STEP_DEFINITIONS = [
    (1, "Precision CNC Machining", "FABRICATION", "CNC_MILL", False, 120),
    (2, "Sub-Assembly Insertion", "ASSEMBLY", "SMT_PICK_PLACE", False, 45),
    (3, "Structural Laser Welding", "ASSEMBLY", "LASER_WELDER", True, 90),
    (4, "Protective Polymer Coating", "TREATMENT", "INJECTION_MOLD", False, 180),
    (5, "Automated Quality Gate Testing", "TESTING", "OPTICAL_INSPECTOR", True, 60),
    (6, "Final Unit Packaging", "PACKAGING", "OPTICAL_INSPECTOR", False, 30),
]


def generate_master_data(profile: DatasetProfile, master_seed: int) -> Dict[str, Any]:
    """Deterministically generates all master data entities."""
    prng = random.Random(derive_subseed(master_seed, "master_data"))

    # 1. Products: Half Finished Goods, Half Raw Materials
    products: List[Dict[str, Any]] = []
    fg_count = profile.product_count // 2
    rm_count = profile.product_count - fg_count

    fg_products: List[Dict[str, Any]] = []
    rm_products: List[Dict[str, Any]] = []

    for i in range(1, fg_count + 1):
        pid = format_sku_id(i)
        p = {
            "product_id": pid,
            "sku": pid,
            "product_name": f"Precision Actuator Assembly Unit {i:03d}",
            "product_type": "FINISHED_GOOD",
            "revision": "A",
            "base_uom": "EA",
            "lifecycle_state": "ACTIVE",
            "effective_start_date": (BASE_EPOCH + timedelta(days=-180)).date().isoformat(),
            "effective_end_date": None,
            "created_at": (BASE_EPOCH + timedelta(days=-180, minutes=i * 10)).isoformat(),
        }
        products.append(p)
        fg_products.append(p)

    for i in range(1, rm_count + 1):
        idx = fg_count + i
        pid = format_sku_id(idx)
        rm_names = ["Titanium Alloy Billet", "Ceramic Insulator Ring", "Precision Micro-Bearing", "High-Conductivity Copper Wire", "Polymer Sealing O-Ring"]
        name = f"{rm_names[(i - 1) % len(rm_names)]} Type-{i:02d}"
        p = {
            "product_id": pid,
            "sku": pid,
            "product_name": name,
            "product_type": "RAW_MATERIAL",
            "revision": "A",
            "base_uom": "EA" if (i % 2 == 1) else "KG",
            "lifecycle_state": "ACTIVE",
            "effective_start_date": (BASE_EPOCH + timedelta(days=-365)).date().isoformat(),
            "effective_end_date": None,
            "created_at": (BASE_EPOCH + timedelta(days=-365, minutes=i * 15)).isoformat(),
        }
        products.append(p)
        rm_products.append(p)

    # 2. Suppliers
    suppliers: List[Dict[str, Any]] = []
    tiers = ["TIER_1_LOW", "TIER_2_MED", "TIER_3_HIGH"]
    tier_weights = [0.60, 0.30, 0.10]

    for i in range(1, profile.supplier_count + 1):
        sid = format_supplier_id(i)
        tier = prng.choices(tiers, weights=tier_weights, k=1)[0]
        s = {
            "supplier_id": sid,
            "supplier_name": f"Apex Industrial Components Global #{i:03d}",
            "supplier_status": "QUALIFIED" if tier != "TIER_3_HIGH" or i % 3 != 0 else "PROBATION",
            "supplier_risk_tier": tier,
            "country_code": COUNTRY_CODES[(i - 1) % len(COUNTRY_CODES)],
            "lead_time_days": 7 + (i % 5) * 7,
            "effective_start_date": (BASE_EPOCH + timedelta(days=-500)).date().isoformat(),
            "effective_end_date": None,
        }
        suppliers.append(s)

    # 3. BOM & BOM Lines
    boms: List[Dict[str, Any]] = []
    bom_lines: List[Dict[str, Any]] = []
    bom_line_seq = 1

    for i, fg in enumerate(fg_products, 1):
        bid = format_bom_id(i)
        bom = {
            "bom_id": bid,
            "product_id": fg["product_id"],
            "revision": "A",
            "status": "ACTIVE",
            "effective_start_date": fg["effective_start_date"],
            "effective_end_date": None,
        }
        boms.append(bom)

        # Assign 2 to 4 raw materials to each BOM
        assigned_rm_count = 2 + (i % 3)
        assigned_rms = [rm_products[(i + offset) % len(rm_products)] for offset in range(assigned_rm_count)]

        for rm in assigned_rms:
            bl_id = format_bom_line_id(bom_line_seq)
            bl = {
                "bom_line_id": bl_id,
                "bom_id": bid,
                "material_product_id": rm["product_id"],
                "quantity_per_unit": float(round(1.0 + (bom_line_seq % 3) * 0.5, 4)),
                "uom": rm["base_uom"],
                "scrap_factor": float(round(0.01 + (bom_line_seq % 4) * 0.01, 4)),
                "is_required": True,
                "effective_start_date": bom["effective_start_date"],
                "effective_end_date": None,
            }
            bom_lines.append(bl)
            bom_line_seq += 1

    # 4. Machines
    machines: List[Dict[str, Any]] = []
    lines = ["LINE-A", "LINE-B", "LINE-C"]
    for i in range(1, profile.machine_count + 1):
        mid = format_machine_id(i)
        m_def = MACHINE_DEFINITIONS[(i - 1) % len(MACHINE_DEFINITIONS)]
        m = {
            "machine_id": mid,
            "machine_name": f"{m_def[1]} #{i:02d}",
            "machine_type": m_def[0],
            "line_code": lines[(i - 1) % len(lines)],
            "machine_status": "OPERATIONAL" if i % 10 != 0 else "DEGRADED",
            "calibration_due_date": (BASE_EPOCH + timedelta(days=90 + (i * 12))).date().isoformat(),
            "maintenance_risk_score": float(round(5.0 + (i % 8) * 8.5, 2)),
        }
        machines.append(m)

    # 5. Process Steps
    process_steps: List[Dict[str, Any]] = []
    steps_to_create = STEP_DEFINITIONS[: profile.process_step_count]
    for step_data in steps_to_create:
        seq, name, stype, allowed_m, is_gate, cycle_time = step_data
        sid = format_process_step_id(seq)
        step = {
            "process_step_id": sid,
            "step_sequence": seq,
            "step_name": name,
            "step_type": stype,
            "is_quality_gate": is_gate,
            "standard_cycle_time_seconds": cycle_time,
            "allowed_machine_type": allowed_m,
        }
        process_steps.append(step)

    # 6. Inspection Plans
    inspection_plans: List[Dict[str, Any]] = []
    plan_seq = 1
    quality_gate_steps = [s for s in process_steps if s["is_quality_gate"]]
    if not quality_gate_steps:
        quality_gate_steps = [process_steps[-1]]

    for fg in fg_products:
        for q_step in quality_gate_steps:
            pid = format_inspection_plan_id(plan_seq)
            plan = {
                "inspection_plan_id": pid,
                "product_id": fg["product_id"],
                "process_step_id": q_step["process_step_id"],
                "inspection_type": "FINAL" if q_step["step_sequence"] == process_steps[-1]["step_sequence"] else "IN_PROCESS",
                "sampling_rule": "ANSI_ASQ_Z1_4",
                "acceptance_limit": 0.015,
                "defect_categories": '["DIMENSIONAL", "SURFACE_FINISH", "ELECTRICAL", "ASSEMBLY_ALIGNMENT"]',
                "effective_start_date": fg["effective_start_date"],
                "effective_end_date": None,
                "plan_status": "ACTIVE",
            }
            inspection_plans.append(plan)
            plan_seq += 1

    return {
        "products": products,
        "fg_products": fg_products,
        "rm_products": rm_products,
        "suppliers": suppliers,
        "boms": boms,
        "bom_lines": bom_lines,
        "machines": machines,
        "process_steps": process_steps,
        "inspection_plans": inspection_plans,
    }
