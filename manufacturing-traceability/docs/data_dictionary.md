# Field-Level Data Dictionary
## Manufacturing Defect-Traceability System

All data generated in this solution is synthetic, non-sensitive, and governed by deterministic rules rooted in master seed `20261022` and base epoch `2026-01-01T00:00:00Z`.

---

## 1. Product (`products`)

| Field Name | Description | Data Type | Required | Allowed Values / Format | UoM | Unique | Default | Validation / Reconciliation Rule | Source/Derived | Sensitivity |
|---|---|---|---|---|---|---|---|---|---|---|
| `product_id` | Canonical primary key for product | VARCHAR(32) | Yes | `SKU-\d{6}` (e.g. `SKU-000001`) | - | PK | - | Deterministic sequence | Source | Synthetic |
| `sku` | Aligned SKU code | VARCHAR(64) | Yes | `SKU-\d{6}` | - | Yes | - | Must match `product_id` | Source | Synthetic |
| `product_name` | Synthetic product name | VARCHAR(255) | Yes | Text (1-255 chars) | - | No | - | Synthetic naming template | Source | Synthetic |
| `product_type` | Product classification | VARCHAR(32) | Yes | `FINISHED_GOOD`, `RAW_MATERIAL` | - | No | - | Controlled vocabulary | Source | Synthetic |
| `revision` | Engineering revision | VARCHAR(16) | Yes | `A`, `B`, `C` | - | No | `A` | Alphanumeric revision | Source | Synthetic |
| `base_uom` | Base unit of measure | VARCHAR(16) | Yes | `EA`, `KG`, `M`, `L` | - | No | `EA` | Controlled UoM enum | Source | Synthetic |
| `lifecycle_state` | Current state | VARCHAR(32) | Yes | `ACTIVE`, `OBSOLETE`, `DRAFT` | - | No | `ACTIVE` | Governed status | Derived | Synthetic |
| `effective_start_date`| Date product becomes active | DATE | Yes | `YYYY-MM-DD` | - | No | - | Start $\le$ End date | Source | Synthetic |
| `effective_end_date` | Date product is retired | DATE | No | `YYYY-MM-DD` | - | No | NULL | Nullable (open-ended) | Source | Synthetic |
| `created_at` | Record creation timestamp | TIMESTAMPTZ | Yes | ISO 8601 | - | No | - | Deterministic timestamp | Source | Synthetic |

---

## 2. BOM & BOM Lines (`boms`, `bom_lines`)

### BOM (`boms`)
| Field Name | Description | Data Type | Required | Allowed Values / Format | UoM | Unique | Default | Validation / Reconciliation Rule | Source/Derived | Sensitivity |
|---|---|---|---|---|---|---|---|---|---|---|
| `bom_id` | Primary key for BOM | VARCHAR(32) | Yes | `BOM-\d{6}` | - | PK | - | Deterministic sequence | Source | Synthetic |
| `product_id` | Finished good reference | VARCHAR(32) | Yes | FK to `products.product_id` | - | No | - | Must refer to `FINISHED_GOOD` | Source | Synthetic |
| `revision` | Engineering revision | VARCHAR(16) | Yes | `A`, `B` | - | No | `A` | Matches product revision | Source | Synthetic |
| `status` | BOM operational state | VARCHAR(32) | Yes | `ACTIVE`, `SUPERSEDED`, `DRAFT` | - | No | `ACTIVE` | Controlled enum | Source | Synthetic |
| `effective_start_date`| Effective start | DATE | Yes | `YYYY-MM-DD` | - | No | - | Non-overlapping for same product | Source | Synthetic |
| `effective_end_date` | Effective end | DATE | No | `YYYY-MM-DD` | - | No | NULL | Start $\le$ End | Source | Synthetic |

### BOMLine (`bom_lines`)
| Field Name | Description | Data Type | Required | Allowed Values / Format | UoM | Unique | Default | Validation / Reconciliation Rule | Source/Derived | Sensitivity |
|---|---|---|---|---|---|---|---|---|---|---|
| `bom_line_id` | Primary key for BOM line | VARCHAR(32) | Yes | `BOML-\d{6}` | - | PK | - | Deterministic sequence | Source | Synthetic |
| `bom_id` | Parent BOM reference | VARCHAR(32) | Yes | FK to `boms.bom_id` | - | No | - | Valid BOM reference | Source | Synthetic |
| `material_product_id` | Component product reference | VARCHAR(32) | Yes | FK to `products.product_id` | - | No | - | Must refer to `RAW_MATERIAL` | Source | Synthetic |
| `quantity_per_unit` | Required component qty | NUMERIC(12,4) | Yes | $> 0.0000$ | Variable | No | `1.0` | Positive quantity | Source | Synthetic |
| `uom` | Component UoM | VARCHAR(16) | Yes | `EA`, `KG`, `M`, `L` | - | No | `EA` | Matches component UoM | Source | Synthetic |
| `scrap_factor` | Expected scrap ratio | NUMERIC(6,4) | Yes | $[0.00, 0.50]$ | Ratio | No | `0.02` | Permitted scrap allowance | Source | Synthetic |
| `is_required` | Mandatory flag | BOOLEAN | Yes | `TRUE`, `FALSE` | - | No | `TRUE` | Must be consumed for completed order | Source | Synthetic |
| `effective_start_date`| Effective start | DATE | Yes | `YYYY-MM-DD` | - | No | - | Within BOM date range | Source | Synthetic |
| `effective_end_date` | Effective end | DATE | No | `YYYY-MM-DD` | - | No | NULL | Start $\le$ End | Source | Synthetic |

---

## 3. Supplier (`suppliers`)

| Field Name | Description | Data Type | Required | Allowed Values / Format | UoM | Unique | Default | Validation / Reconciliation Rule | Source/Derived | Sensitivity |
|---|---|---|---|---|---|---|---|---|---|---|
| `supplier_id` | Supplier identifier | VARCHAR(32) | Yes | `SUP-\d{4}` (e.g. `SUP-0001`) | - | PK | - | Deterministic sequence | Source | Synthetic |
| `supplier_name` | Synthetic vendor name | VARCHAR(255) | Yes | Text (1-255 chars) | - | Yes | - | Synthetic naming template | Source | Synthetic |
| `supplier_status` | Qualification status | VARCHAR(32) | Yes | `QUALIFIED`, `PROBATION`, `SUSPENDED` | - | No | `QUALIFIED` | Controlled enum | Source | Synthetic |
| `supplier_risk_tier` | Quality risk tier | VARCHAR(32) | Yes | `TIER_1_LOW`, `TIER_2_MED`, `TIER_3_HIGH` | - | No | `TIER_1_LOW` | Determines defect probability | Source | Synthetic |
| `country_code` | ISO country code | VARCHAR(2) | Yes | ISO 3166-1 alpha-2 (`US`, `DE`, `JP`, etc.) | - | No | - | Valid 2-letter country code | Source | Synthetic |
| `lead_time_days` | Nominal delivery lead | INTEGER | Yes | $> 0$ | Days | No | `14` | Positive integer | Source | Synthetic |
| `effective_start_date`| Inception date | DATE | Yes | `YYYY-MM-DD` | - | No | - | Start $\le$ End | Source | Synthetic |
| `effective_end_date` | Termination date | DATE | No | `YYYY-MM-DD` | - | No | NULL | Start $\le$ End | Source | Synthetic |

---

## 4. MaterialLot (`material_lots`)

| Field Name | Description | Data Type | Required | Allowed Values / Format | UoM | Unique | Default | Validation / Reconciliation Rule | Source/Derived | Sensitivity |
|---|---|---|---|---|---|---|---|---|---|---|
| `material_lot_id` | Lot identifier | VARCHAR(64) | Yes | `LOT-SUP-\d{4}-\d{4}-\d{6}` | - | PK | - | Strict format: `LOT-SUP-0001-2026-000001` | Source | Synthetic |
| `supplier_id` | Vendor reference | VARCHAR(32) | Yes | FK to `suppliers.supplier_id` | - | No | - | Valid Supplier reference | Source | Synthetic |
| `material_product_id` | Product reference | VARCHAR(32) | Yes | FK to `products.product_id` | - | No | - | Must be `RAW_MATERIAL` | Source | Synthetic |
| `supplier_batch_code`| Manufacturer batch | VARCHAR(64) | Yes | Alphanumeric batch string | - | No | - | Synthetic batch code | Source | Synthetic |
| `received_date` | Date delivered | DATE | Yes | `YYYY-MM-DD` | - | No | - | Received $\le$ Expiry | Source | Synthetic |
| `expiry_date` | Shelf life expiry | DATE | Yes | `YYYY-MM-DD` | - | No | - | Expiry $>$ Received | Source | Synthetic |
| `received_quantity` | Total inwarded qty | NUMERIC(14,4) | Yes | $> 0.0000$ | UoM | No | - | Initial received quantity | Source | Synthetic |
| `available_quantity` | Available uncommitted | NUMERIC(14,4) | Yes | $\ge 0.0000$ | UoM | No | - | `received - consumed - rejected - quarantined` | Derived | Synthetic |
| `consumed_quantity` | Depleted quantity | NUMERIC(14,4) | Yes | $\ge 0.0000$ | UoM | No | `0.0` | Sum of related consumptions | Derived | Synthetic |
| `rejected_quantity` | Quality rejected qty | NUMERIC(14,4) | Yes | $\ge 0.0000$ | UoM | No | `0.0` | Inward inspection reject | Derived | Synthetic |
| `quarantined_quantity`| Isolated quantity | NUMERIC(14,4) | Yes | $\ge 0.0000$ | UoM | No | `0.0` | Under quality hold | Derived | Synthetic |
| `uom` | Lot unit of measure | VARCHAR(16) | Yes | `EA`, `KG`, `M`, `L` | - | No | - | Matches raw material base UoM | Source | Synthetic |
| `lot_status` | Current lot state | VARCHAR(32) | Yes | Controlled lot status enum | - | No | `RECEIVED` | Latest StateEvent | Derived | Synthetic |
| `incoming_quality_score` | Inward quality rating | NUMERIC(5,2) | Yes | $[0.00, 100.00]$ | Score | No | `95.00` | Correlated with supplier risk | Source | Synthetic |

---

## 5. ProductionOrder (`production_orders`)

| Field Name | Description | Data Type | Required | Allowed Values / Format | UoM | Unique | Default | Validation / Reconciliation Rule | Source/Derived | Sensitivity |
|---|---|---|---|---|---|---|---|---|---|---|
| `production_order_id` | Work order ID | VARCHAR(32) | Yes | `WO-\d{4}-\d{6}` (e.g. `WO-2026-000001`) | - | PK | - | Deterministic sequence | Source | Synthetic |
| `product_id` | Product produced | VARCHAR(32) | Yes | FK to `products.product_id` | - | No | - | Must be `FINISHED_GOOD` | Source | Synthetic |
| `planned_quantity` | Planned run quantity | NUMERIC(12,2) | Yes | $> 0.00$ | EA | No | - | Target order output | Source | Synthetic |
| `completed_quantity` | Total units completed | NUMERIC(12,2) | Yes | $\ge 0.00$ | EA | No | `0.00` | `accepted + rework + scrap + quarantined` | Derived | Synthetic |
| `accepted_quantity` | Conforming units | NUMERIC(12,2) | Yes | $\ge 0.00$ | EA | No | `0.00` | Completed conforming units | Derived | Synthetic |
| `rework_quantity` | Reworked units | NUMERIC(12,2) | Yes | $\ge 0.00$ | EA | No | `0.00` | Units routed to rework | Derived | Synthetic |
| `scrap_quantity` | Scrapped units | NUMERIC(12,2) | Yes | $\ge 0.00$ | EA | No | `0.00` | Unrecoverable scrap units | Derived | Synthetic |
| `quarantined_quantity`| Quarantined units | NUMERIC(12,2) | Yes | $\ge 0.00$ | EA | No | `0.00` | WIP units under hold | Derived | Synthetic |
| `order_status` | Current order state | VARCHAR(32) | Yes | Controlled order status enum | - | No | `PLANNED` | Latest StateEvent | Derived | Synthetic |
| `planned_start_date`| Planned start | DATE | Yes | `YYYY-MM-DD` | - | No | - | Planned start $\le$ Planned end | Source | Synthetic |
| `planned_end_date` | Planned completion | DATE | Yes | `YYYY-MM-DD` | - | No | - | Planned end $\ge$ Planned start | Source | Synthetic |
| `actual_start_date` | Actual start | DATE | No | `YYYY-MM-DD` | - | No | NULL | Actual start $\le$ Actual end | Derived | Synthetic |
| `actual_end_date` | Actual completion | DATE | No | `YYYY-MM-DD` | - | No | NULL | Actual end $\ge$ Actual start | Derived | Synthetic |
| `production_lot_code`| Outward lot code | VARCHAR(64) | Yes | `LOT-PROD-\d{4}-\d{6}` | - | Yes | - | Internal lot tracking code | Source | Synthetic |

---

## 6. MaterialConsumption (`material_consumptions`)

| Field Name | Description | Data Type | Required | Allowed Values / Format | UoM | Unique | Default | Validation / Reconciliation Rule | Source/Derived | Sensitivity |
|---|---|---|---|---|---|---|---|---|---|---|
| `consumption_id` | Consumption transaction | VARCHAR(32) | Yes | `CONS-\d{6}` | - | PK | - | Deterministic sequence | Source | Synthetic |
| `production_order_id`| Consuming order | VARCHAR(32) | Yes | FK to `production_orders` | - | No | - | Valid order reference | Source | Synthetic |
| `material_lot_id` | Consumed lot | VARCHAR(64) | Yes | FK to `material_lots` | - | No | - | Valid material lot reference | Source | Synthetic |
| `bom_line_id` | Implicated BOM line | VARCHAR(32) | Yes | FK to `bom_lines` | - | No | - | Valid BOM line reference | Source | Synthetic |
| `consumed_quantity` | Quantity depleted | NUMERIC(14,4) | Yes | $> 0.0000$ | UoM | No | - | Increments lot consumed balance | Source | Synthetic |
| `uom` | Unit of measure | VARCHAR(16) | Yes | `EA`, `KG`, `M`, `L` | - | No | `EA` | Matches lot UoM | Source | Synthetic |
| `consumed_at` | Transaction time | TIMESTAMPTZ | Yes | ISO 8601 | - | No | - | Deterministic logical timestamp | Source | Synthetic |
| `consumption_status` | Status | VARCHAR(32) | Yes | `COMMITTED`, `REVERSED` | - | No | `COMMITTED` | Transaction state | Source | Synthetic |

---

## 7. Machine & Process (`machines`, `process_steps`, `process_executions`)

### Machine (`machines`)
| Field Name | Description | Data Type | Required | Allowed Values / Format | UoM | Unique | Default | Validation / Reconciliation Rule | Source/Derived | Sensitivity |
|---|---|---|---|---|---|---|---|---|---|---|
| `machine_id` | Primary key | VARCHAR(32) | Yes | `MCH-\d{4}` | - | PK | - | Deterministic sequence | Source | Synthetic |
| `machine_name` | Machine name | VARCHAR(255) | Yes | Text (1-255 chars) | - | No | - | Synthetic naming | Source | Synthetic |
| `machine_type` | Machine classification | VARCHAR(32) | Yes | Controlled machine type enum | - | No | - | Matched to process steps | Source | Synthetic |
| `line_code` | Line assignment | VARCHAR(32) | Yes | `LINE-A`, `LINE-B`, `LINE-C` | - | No | `LINE-A` | Physical line identifier | Source | Synthetic |
| `machine_status` | Operational state | VARCHAR(32) | Yes | `OPERATIONAL`, `MAINTENANCE`, `DEGRADED`, `OFFLINE` | - | No | `OPERATIONAL` | Controlled enum | Source | Synthetic |
| `calibration_due_date`| Next calibration | DATE | Yes | `YYYY-MM-DD` | - | No | - | Future date | Source | Synthetic |
| `maintenance_risk_score`| Wear/risk index | NUMERIC(5,2) | Yes | $[0.00, 100.00]$ | Score | No | `10.0` | Drives drift window calculation | Source | Synthetic |

### ProcessStep (`process_steps`)
| Field Name | Description | Data Type | Required | Allowed Values / Format | UoM | Unique | Default | Validation / Reconciliation Rule | Source/Derived | Sensitivity |
|---|---|---|---|---|---|---|---|---|---|---|
| `process_step_id` | Primary key | VARCHAR(32) | Yes | `STEP-\d{4}` | - | PK | - | Deterministic sequence | Source | Synthetic |
| `step_sequence` | Route sequence | INTEGER | Yes | $> 0$ | - | No | - | Monotonic routing index | Source | Synthetic |
| `step_name` | Operation name | VARCHAR(255) | Yes | Text (1-255 chars) | - | No | - | Synthetic naming | Source | Synthetic |
| `step_type` | Operation type | VARCHAR(32) | Yes | Controlled step type enum | - | No | - | Controlled enum | Source | Synthetic |
| `is_quality_gate` | Quality gate flag | BOOLEAN | Yes | `TRUE`, `FALSE` | - | No | `FALSE` | Requires formal inspection | Source | Synthetic |
| `standard_cycle_time_seconds`| Nominal duration | INTEGER | Yes | $> 0$ | Seconds | No | `60` | Positive cycle duration | Source | Synthetic |
| `allowed_machine_type`| Required machine | VARCHAR(32) | Yes | Matches `machine_type` | - | No | - | Machine compatibility gate | Source | Synthetic |

### ProcessExecution (`process_executions`)
| Field Name | Description | Data Type | Required | Allowed Values / Format | UoM | Unique | Default | Validation / Reconciliation Rule | Source/Derived | Sensitivity |
|---|---|---|---|---|---|---|---|---|---|---|
| `process_execution_id`| Primary key | VARCHAR(32) | Yes | `PEX-\d{6}` | - | PK | - | Deterministic sequence | Source | Synthetic |
| `production_order_id`| Parent order | VARCHAR(32) | Yes | FK to `production_orders` | - | No | - | Valid order reference | Source | Synthetic |
| `process_step_id` | Executed step | VARCHAR(32) | Yes | FK to `process_steps` | - | No | - | Valid step reference | Source | Synthetic |
| `machine_id` | Machine used | VARCHAR(32) | Yes | FK to `machines` | - | No | - | Must match allowed machine type | Source | Synthetic |
| `execution_start_at` | Start timestamp | TIMESTAMPTZ | Yes | ISO 8601 | - | No | - | Start $\le$ End | Source | Synthetic |
| `execution_end_at` | Completion timestamp| TIMESTAMPTZ | Yes | ISO 8601 | - | No | - | End $\ge$ Start | Source | Synthetic |
| `input_quantity` | Input batch size | NUMERIC(12,2) | Yes | $> 0.00$ | EA | No | - | `output + scrap + quarantined + rework` | Source | Synthetic |
| `output_quantity` | Yielded batch size | NUMERIC(12,2) | Yes | $\ge 0.00$ | EA | No | - | Conforming yielded units | Derived | Synthetic |
| `rework_quantity` | Step rework units | NUMERIC(12,2) | Yes | $\ge 0.00$ | EA | No | `0.00` | Diverted to rework | Derived | Synthetic |
| `scrap_quantity` | Step scrap units | NUMERIC(12,2) | Yes | $\ge 0.00$ | EA | No | `0.00` | Condemned to scrap | Derived | Synthetic |
| `quarantined_quantity`| Step quarantined | NUMERIC(12,2) | Yes | $\ge 0.00$ | EA | No | `0.00` | Quarantined units | Derived | Synthetic |
| `execution_status` | Status | VARCHAR(32) | Yes | `IN_PROGRESS`, `COMPLETED`, `ABORTED` | - | No | `COMPLETED` | Controlled enum | Source | Synthetic |
| `drift_indicator` | Drift condition | BOOLEAN | Yes | `TRUE`, `FALSE` | - | No | `FALSE` | Deterministic machine drift flag | Source | Synthetic |
| `process_measurement`| Physical measurement| NUMERIC(10,3) | Yes | Numeric reading | Units | No | - | Deterministic physical reading | Source | Synthetic |

---

## 8. Inspection (`inspection_plans`, `inspection_results`)

### InspectionPlan (`inspection_plans`)
| Field Name | Description | Data Type | Required | Allowed Values / Format | UoM | Unique | Default | Validation / Reconciliation Rule | Source/Derived | Sensitivity |
|---|---|---|---|---|---|---|---|---|---|---|
| `inspection_plan_id` | Primary key | VARCHAR(32) | Yes | `PLAN-\d{4}` | - | PK | - | Deterministic sequence | Source | Synthetic |
| `product_id` | Governed product | VARCHAR(32) | Yes | FK to `products` | - | No | - | Finished good reference | Source | Synthetic |
| `process_step_id` | Governed step | VARCHAR(32) | Yes | FK to `process_steps` | - | No | - | Quality gate step | Source | Synthetic |
| `inspection_type` | Inspection scope | VARCHAR(32) | Yes | Controlled inspection type | - | No | `IN_PROCESS` | Controlled enum | Source | Synthetic |
| `sampling_rule` | Sampling method | VARCHAR(32) | Yes | Controlled sampling rule | - | No | `ANSI_ASQ_Z1_4` | Controlled enum | Source | Synthetic |
| `acceptance_limit` | Max defect ratio | NUMERIC(6,4) | Yes | $[0.0000, 1.0000]$ | Ratio | No | `0.01` | Acceptance threshold | Source | Synthetic |
| `defect_categories` | Monitored classes | TEXT | Yes | JSON array string | - | No | `[]` | Monitored defect categories | Source | Synthetic |
| `effective_start_date`| Effective start | DATE | Yes | `YYYY-MM-DD` | - | No | - | Start $\le$ End | Source | Synthetic |
| `effective_end_date` | Effective end | DATE | No | `YYYY-MM-DD` | - | No | NULL | Start $\le$ End | Source | Synthetic |
| `plan_status` | Operational state | VARCHAR(32) | Yes | `ACTIVE`, `REVISED`, `RETIRED` | - | No | `ACTIVE` | Controlled enum | Source | Synthetic |

### InspectionResult (`inspection_results`)
| Field Name | Description | Data Type | Required | Allowed Values / Format | UoM | Unique | Default | Validation / Reconciliation Rule | Source/Derived | Sensitivity |
|---|---|---|---|---|---|---|---|---|---|---|
| `inspection_result_id`| Primary key | VARCHAR(64) | Yes | `INSP-WO-\d{4}-\d{6}-\d{3}` | - | PK | - | Strict format: `INSP-WO-2026-000001-001` | Source | Synthetic |
| `inspection_plan_id` | Governed plan | VARCHAR(32) | Yes | FK to `inspection_plans` | - | No | - | Valid plan reference | Source | Synthetic |
| `production_order_id`| Evaluated order | VARCHAR(32) | Yes | FK to `production_orders` | - | No | - | Valid order reference | Source | Synthetic |
| `process_execution_id`| Checked execution | VARCHAR(32) | Yes | FK to `process_executions` | - | No | - | Valid execution reference | Source | Synthetic |
| `inspected_at` | Inspection time | TIMESTAMPTZ | Yes | ISO 8601 | - | No | - | Deterministic timestamp | Source | Synthetic |
| `inspected_quantity` | Total sample size | NUMERIC(12,2) | Yes | $> 0.00$ | EA | No | - | `accepted_quantity + rejected_quantity` (strict denominator) | Source | Synthetic |
| `accepted_quantity` | Conforming sample | NUMERIC(12,2) | Yes | $\ge 0.00$ | EA | No | - | Conforming sample units | Derived | Synthetic |
| `rejected_quantity` | Rejected sample | NUMERIC(12,2) | Yes | $\ge 0.00$ | EA | No | `0.00` | `reworked + scrapped + quarantined` | Derived | Synthetic |
| `reworked_quantity` | Sample rework | NUMERIC(12,2) | Yes | $\ge 0.00$ | EA | No | `0.00` | Diverted to rework | Derived | Synthetic |
| `scrapped_quantity` | Sample scrap | NUMERIC(12,2) | Yes | $\ge 0.00$ | EA | No | `0.00` | Condemned to scrap | Derived | Synthetic |
| `quarantined_quantity`| Sample quarantine| NUMERIC(12,2) | Yes | $\ge 0.00$ | EA | No | `0.00` | Quarantined sample | Derived | Synthetic |
| `inspection_status` | Status | VARCHAR(32) | Yes | `PENDING`, `COMPLETED` | - | No | `COMPLETED` | Latest StateEvent | Derived | Synthetic |
| `disposition` | Disposition | VARCHAR(32) | Yes | `ACCEPTED`, `REJECTED`, `CONDITIONAL_ACCEPTANCE` | - | No | `ACCEPTED` | Controlled enum | Derived | Synthetic |
| `defect_rate` | Defect proportion | NUMERIC(6,4) | Yes | $[0.0000, 1.0000]$ | Ratio | No | `0.0000` | `rejected_quantity / inspected_quantity` | Derived | Synthetic |

---

## 9. StateEvent (`state_events`)

| Field Name | Description | Data Type | Required | Allowed Values / Format | UoM | Unique | Default | Validation / Reconciliation Rule | Source/Derived | Sensitivity |
|---|---|---|---|---|---|---|---|---|---|---|
| `event_id` | Primary key | VARCHAR(32) | Yes | `EVT-\d{8}` (e.g. `EVT-00000001`) | - | PK | - | Deterministic sequence | Source | Synthetic |
| `entity_type` | Target table | VARCHAR(32) | Yes | Controlled entity type enum | - | No | - | Target table identifier | Source | Synthetic |
| `entity_id` | Target entity ID | VARCHAR(64) | Yes | Target entity PK string | - | No | - | References entity identifier | Source | Synthetic |
| `material_lot_id` | Typed lot FK | VARCHAR(64) | No | FK to `material_lots` | - | No | NULL | Populated if entity is lot | Source | Synthetic |
| `production_order_id`| Typed order FK | VARCHAR(32) | No | FK to `production_orders` | - | No | NULL | Populated if entity is order | Source | Synthetic |
| `inspection_result_id`| Typed inspection FK| VARCHAR(64) | No | FK to `inspection_results` | - | No | NULL | Populated if entity is inspection | Source | Synthetic |
| `defect_id` | Typed defect FK | VARCHAR(32) | No | FK to `defects` | - | No | NULL | Populated if entity is defect | Source | Synthetic |
| `corrective_action_id`| Typed CAPA FK | VARCHAR(32) | No | FK to `corrective_actions` | - | No | NULL | Populated if entity is CAPA | Source | Synthetic |
| `event_sequence` | Event sequence | INTEGER | Yes | $> 0$ ($1, 2, 3, \dots$) | - | No | - | Immutable per-entity sequence | Source | Synthetic |
| `previous_state` | Preceding status | VARCHAR(32) | No | Status enum string | - | No | NULL | Preceding lifecycle state | Source | Synthetic |
| `new_state` | Resulting status | VARCHAR(32) | Yes | Status enum string | - | No | - | Transitioned lifecycle state | Source | Synthetic |
| `event_timestamp` | Occurrence time | TIMESTAMPTZ | Yes | ISO 8601 | - | No | - | Deterministic logical timestamp | Source | Synthetic |
| `actor_role` | Actor | VARCHAR(32) | Yes | Controlled role enum | - | No | `SYSTEM` | Role performing change | Source | Synthetic |
| `reason_code` | Audit reason | VARCHAR(64) | Yes | Standardized reason code | - | No | `NORMAL_FLOW` | Audit justification | Source | Synthetic |
| `event_notes` | Narrative | TEXT | No | Free text | - | No | NULL | Explanatory context | Source | Synthetic |

*(Constraint: Exactly one typed foreign-key column must be non-null; unique constraint on `(entity_type, entity_id, event_sequence)`).*
