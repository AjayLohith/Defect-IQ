# Anomaly Catalog & Ground Truth Reference
## Manufacturing Defect-Traceability System

This catalog details the five deliberate negative scenarios, their safe design, their injection mechanisms, their detection strategies, and the corresponding ground-truth definitions.

Authoritative ground truth is stored exclusively in `artifacts/ground_truth/ground_truth.csv` and `artifacts/ground_truth/ground_truth.json`. Operational schemas and UI workflows do not expose ground-truth labels.

---

## Anomaly Matrix

| Anomaly ID | Classification (`anomaly_type`) | Target Entity | Targeted Attribute | Detection Rule | Safe Relational Mechanism |
|---|---|---|---|---|---|
| **ANOMALY-001** | `NONEXISTENT_REPORTED_LOT` | `Defect` (`DEF-2026-000001`) | `reported_material_lot_id = 'LOT-SUP-9999-2026-999999'` | `VAL_DEFECT_REPORTED_LOT_EXISTS` | Normalized `material_lot_id` set to `NULL` (FK valid), invalid string stored in raw reported field. |
| **ANOMALY-002** | `MISSING_BOM_CONSUMPTION` | `ProductionOrder` (`WO-2026-000001`) | Omitted `MaterialConsumption` for required `BOMLine` | `VAL_ORDER_BOM_CONSUMPTION_COMPLETE` | Order marked `COMPLETED` but one mandatory BOM component has 0 consumption transactions. |
| **ANOMALY-003** | `PREMATURE_CAPA_CLOSURE` | `CorrectiveAction` (`CAPA-2026-000005`) | `StateEvent(new_state='CLOSED')` with no passed verification | `VAL_CAPA_CLOSURE_REQUIRES_VERIFICATION` | Injected directly via test fixture/generator; API unconditionally rejects this transition. |
| **ANOMALY-004** | `DEFECT_QUANTITY_EXCEEDS_INSPECTED` | `Defect` (`DEF-2026-000002`) | `defect_quantity = 170.0` vs parent `inspected_quantity = 20.0` | `VAL_DEFECT_QUANTITY_LE_INSPECTED` | Quantities stored as valid decimals, arithmetic impossibility flagged by validator. |
| **ANOMALY-005** | `BROKEN_TRACEABILITY_CHAIN` | `Defect` (`DEF-2026-000003`) | `process_execution_id = 'PEX-000001'` (belongs to `WO-2026-000001`, while Defect is attributed to `WO-2026-000024`) | `VAL_DEFECT_PROCESS_EXECUTION_ORDER_MATCH` | Both FKs are valid in the DB, but cross-order execution mismatch breaks logical trace. |

---

## Detailed Scenario Walkthroughs

### 1. ANOMALY-001: Nonexistent Reported Lot
- **Business Problem**: An operator on the shop floor records a handwritten or mis-scanned lot number that does not match any inwarded lot in the ERP/MES inventory.
- **Data Model Handling**:
  - `defects.material_lot_id`: `NULL` (preserves database referential integrity).
  - `defects.reported_material_lot_id`: `'LOT-SUP-9999-2026-999999'`.
  - `defects.supplier_id`: `NULL`.
- **Validator Decision**:
  - Flags exception: *"Reported lot LOT-SUP-9999-2026-999999 does not exist in material_lots inventory."*

### 2. ANOMALY-002: Missing Mandatory BOM Consumption
- **Business Problem**: A completed production order indicates full yield, but the transaction log reveals that one required raw material component was never backflushed or issued from stores.
- **Data Model Handling**:
  - `production_orders.order_status = 'COMPLETED'`.
  - The order's active BOM contains mandatory component `BOML-000001` (`is_required = True`).
  - No row exists in `material_consumptions` linking `WO-2026-000001` to `BOML-000001`.
- **Validator Decision**:
  - Flags exception: *"Completed order WO-2026-000001 is missing consumption for required BOM line BOML-000001."*

### 3. ANOMALY-003: Premature CAPA Closure
- **Business Problem**: A corrective action is prematurely closed by management without conducting and recording a formal verification audit.
- **Data Model Handling**:
  - `corrective_actions.corrective_action_status = 'CLOSED'`.
  - A `StateEvent` exists with `new_state = 'CLOSED'`.
  - Zero rows exist in `capa_verifications` with `verification_result = 'PASSED'` for this CAPA ID.
  - *Note: Normal API endpoint `POST /api/v1/capas/{id}/close` rejects this action with HTTP 422 `ERR_CAPA_VERIFICATION_REQUIRED`.*
- **Validator Decision**:
  - Flags exception: *"CAPA CAPA-2026-000005 has status CLOSED with zero successful verification records."*

### 4. ANOMALY-004: Defect Quantity Exceeds Inspected Sample
- **Business Problem**: A typographical error or counting failure results in more defects being logged than the total physical units sampled during inspection.
- **Data Model Handling**:
  - Parent `inspection_results.inspected_quantity = 20.0`.
  - Associated `defects.defect_quantity = 170.0`.
- **Validator Decision**:
  - Flags exception: *"Defect DEF-2026-000002 quantity (170.0) exceeds parent inspected sample (20.0)."*

### 5. ANOMALY-005: Broken Traceability Chain (Cross-Order Execution)
- **Business Problem**: A defect logged during an inspection links to a work order, but references a machine execution record from an entirely different production run.
- **Data Model Handling**:
  - `defects.production_order_id = 'WO-2026-000024'`.
  - `defects.process_execution_id = 'PEX-000001'`.
  - In `process_executions`, `PEX-000001.production_order_id = 'WO-2026-000001'`.
  - Both foreign keys resolve to valid records in PostgreSQL, but their relationship graph is inconsistent.
- **Validator Decision**:
  - Flags exception: *"Defect DEF-2026-000003 references ProcessExecution PEX-000001 belonging to order WO-2026-000001, conflicting with Defect order WO-2026-000024."*
