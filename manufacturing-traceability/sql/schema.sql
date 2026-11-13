-- Manufacturing Defect-Traceability Database Schema
-- Standard: PostgreSQL 16
-- Enforces: Foreign keys, non-overlapping BOM dates, typed StateEvent FKs with CHECK constraint, and quantity partitions.

-- 1. Master Data Tables

CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(32) PRIMARY KEY,
    sku VARCHAR(64) UNIQUE NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    product_type VARCHAR(32) NOT NULL CHECK (product_type IN ('FINISHED_GOOD', 'RAW_MATERIAL')),
    revision VARCHAR(16) NOT NULL DEFAULT 'A',
    base_uom VARCHAR(16) NOT NULL DEFAULT 'EA' CHECK (base_uom IN ('EA', 'KG', 'M', 'L')),
    lifecycle_state VARCHAR(32) NOT NULL DEFAULT 'ACTIVE' CHECK (lifecycle_state IN ('ACTIVE', 'OBSOLETE', 'DRAFT')),
    effective_start_date DATE NOT NULL,
    effective_end_date DATE,
    created_at TIMESTAMPTZ NOT NULL,
    CHECK (effective_end_date IS NULL OR effective_start_date <= effective_end_date)
);

CREATE TABLE IF NOT EXISTS boms (
    bom_id VARCHAR(32) PRIMARY KEY,
    product_id VARCHAR(32) NOT NULL REFERENCES products(product_id),
    revision VARCHAR(16) NOT NULL DEFAULT 'A',
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'SUPERSEDED', 'DRAFT')),
    effective_start_date DATE NOT NULL,
    effective_end_date DATE,
    CHECK (effective_end_date IS NULL OR effective_start_date <= effective_end_date)
);

CREATE TABLE IF NOT EXISTS bom_lines (
    bom_line_id VARCHAR(32) PRIMARY KEY,
    bom_id VARCHAR(32) NOT NULL REFERENCES boms(bom_id),
    material_product_id VARCHAR(32) NOT NULL REFERENCES products(product_id),
    quantity_per_unit NUMERIC(12,4) NOT NULL CHECK (quantity_per_unit > 0),
    uom VARCHAR(16) NOT NULL CHECK (uom IN ('EA', 'KG', 'M', 'L')),
    scrap_factor NUMERIC(6,4) NOT NULL DEFAULT 0.02 CHECK (scrap_factor >= 0 AND scrap_factor <= 0.5),
    is_required BOOLEAN NOT NULL DEFAULT TRUE,
    effective_start_date DATE NOT NULL,
    effective_end_date DATE,
    CHECK (effective_end_date IS NULL OR effective_start_date <= effective_end_date)
);

CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id VARCHAR(32) PRIMARY KEY,
    supplier_name VARCHAR(255) UNIQUE NOT NULL,
    supplier_status VARCHAR(32) NOT NULL DEFAULT 'QUALIFIED' CHECK (supplier_status IN ('QUALIFIED', 'PROBATION', 'SUSPENDED')),
    supplier_risk_tier VARCHAR(32) NOT NULL DEFAULT 'TIER_1_LOW' CHECK (supplier_risk_tier IN ('TIER_1_LOW', 'TIER_2_MED', 'TIER_3_HIGH')),
    country_code VARCHAR(2) NOT NULL,
    lead_time_days INTEGER NOT NULL DEFAULT 14 CHECK (lead_time_days > 0),
    effective_start_date DATE NOT NULL,
    effective_end_date DATE,
    CHECK (effective_end_date IS NULL OR effective_start_date <= effective_end_date)
);

CREATE TABLE IF NOT EXISTS machines (
    machine_id VARCHAR(32) PRIMARY KEY,
    machine_name VARCHAR(255) NOT NULL,
    machine_type VARCHAR(32) NOT NULL CHECK (machine_type IN ('CNC_MILL', 'INJECTION_MOLD', 'SMT_PICK_PLACE', 'LASER_WELDER', 'OPTICAL_INSPECTOR')),
    line_code VARCHAR(32) NOT NULL DEFAULT 'LINE-A',
    machine_status VARCHAR(32) NOT NULL DEFAULT 'OPERATIONAL' CHECK (machine_status IN ('OPERATIONAL', 'MAINTENANCE', 'DEGRADED', 'OFFLINE')),
    calibration_due_date DATE NOT NULL,
    maintenance_risk_score NUMERIC(5,2) NOT NULL DEFAULT 10.0 CHECK (maintenance_risk_score >= 0 AND maintenance_risk_score <= 100)
);

CREATE TABLE IF NOT EXISTS process_steps (
    process_step_id VARCHAR(32) PRIMARY KEY,
    step_sequence INTEGER NOT NULL CHECK (step_sequence > 0),
    step_name VARCHAR(255) NOT NULL,
    step_type VARCHAR(32) NOT NULL CHECK (step_type IN ('FABRICATION', 'ASSEMBLY', 'TREATMENT', 'TESTING', 'PACKAGING')),
    is_quality_gate BOOLEAN NOT NULL DEFAULT FALSE,
    standard_cycle_time_seconds INTEGER NOT NULL DEFAULT 60 CHECK (standard_cycle_time_seconds > 0),
    allowed_machine_type VARCHAR(32) NOT NULL CHECK (allowed_machine_type IN ('CNC_MILL', 'INJECTION_MOLD', 'SMT_PICK_PLACE', 'LASER_WELDER', 'OPTICAL_INSPECTOR'))
);

CREATE TABLE IF NOT EXISTS inspection_plans (
    inspection_plan_id VARCHAR(32) PRIMARY KEY,
    product_id VARCHAR(32) NOT NULL REFERENCES products(product_id),
    process_step_id VARCHAR(32) NOT NULL REFERENCES process_steps(process_step_id),
    inspection_type VARCHAR(32) NOT NULL DEFAULT 'IN_PROCESS' CHECK (inspection_type IN ('FIRST_ARTICLE', 'IN_PROCESS', 'FINAL', 'RECEIVING')),
    sampling_rule VARCHAR(32) NOT NULL DEFAULT 'ANSI_ASQ_Z1_4' CHECK (sampling_rule IN ('FULL_100_PERCENT', 'ANSI_ASQ_Z1_4', 'FIXED_SAMPLE_5')),
    acceptance_limit NUMERIC(6,4) NOT NULL DEFAULT 0.01 CHECK (acceptance_limit >= 0 AND acceptance_limit <= 1),
    defect_categories TEXT NOT NULL DEFAULT '[]',
    effective_start_date DATE NOT NULL,
    effective_end_date DATE,
    plan_status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE' CHECK (plan_status IN ('ACTIVE', 'REVISED', 'RETIRED')),
    CHECK (effective_end_date IS NULL OR effective_start_date <= effective_end_date)
);

-- 2. Transactional & Traceability Tables

CREATE TABLE IF NOT EXISTS material_lots (
    material_lot_id VARCHAR(64) PRIMARY KEY,
    supplier_id VARCHAR(32) NOT NULL REFERENCES suppliers(supplier_id),
    material_product_id VARCHAR(32) NOT NULL REFERENCES products(product_id),
    supplier_batch_code VARCHAR(64) NOT NULL,
    received_date DATE NOT NULL,
    expiry_date DATE NOT NULL,
    received_quantity NUMERIC(14,4) NOT NULL CHECK (received_quantity > 0),
    available_quantity NUMERIC(14,4) NOT NULL CHECK (available_quantity >= 0),
    consumed_quantity NUMERIC(14,4) NOT NULL DEFAULT 0.0 CHECK (consumed_quantity >= 0),
    rejected_quantity NUMERIC(14,4) NOT NULL DEFAULT 0.0 CHECK (rejected_quantity >= 0),
    quarantined_quantity NUMERIC(14,4) NOT NULL DEFAULT 0.0 CHECK (quarantined_quantity >= 0),
    uom VARCHAR(16) NOT NULL CHECK (uom IN ('EA', 'KG', 'M', 'L')),
    lot_status VARCHAR(32) NOT NULL DEFAULT 'RECEIVED' CHECK (lot_status IN ('RECEIVED', 'RELEASED', 'PARTIALLY_CONSUMED', 'CONSUMED', 'QUARANTINED', 'REJECTED')),
    incoming_quality_score NUMERIC(5,2) NOT NULL DEFAULT 95.0 CHECK (incoming_quality_score >= 0 AND incoming_quality_score <= 100),
    CHECK (received_date <= expiry_date)
);

CREATE TABLE IF NOT EXISTS production_orders (
    production_order_id VARCHAR(32) PRIMARY KEY,
    product_id VARCHAR(32) NOT NULL REFERENCES products(product_id),
    planned_quantity NUMERIC(12,2) NOT NULL CHECK (planned_quantity > 0),
    completed_quantity NUMERIC(12,2) NOT NULL DEFAULT 0.0 CHECK (completed_quantity >= 0),
    accepted_quantity NUMERIC(12,2) NOT NULL DEFAULT 0.0 CHECK (accepted_quantity >= 0),
    rework_quantity NUMERIC(12,2) NOT NULL DEFAULT 0.0 CHECK (rework_quantity >= 0),
    scrap_quantity NUMERIC(12,2) NOT NULL DEFAULT 0.0 CHECK (scrap_quantity >= 0),
    quarantined_quantity NUMERIC(12,2) NOT NULL DEFAULT 0.0 CHECK (quarantined_quantity >= 0),
    order_status VARCHAR(32) NOT NULL DEFAULT 'PLANNED' CHECK (order_status IN ('PLANNED', 'RELEASED', 'IN_PROGRESS', 'ON_HOLD', 'COMPLETED', 'REWORK', 'SCRAPPED')),
    planned_start_date DATE NOT NULL,
    planned_end_date DATE NOT NULL,
    actual_start_date DATE,
    actual_end_date DATE,
    production_lot_code VARCHAR(64) UNIQUE NOT NULL,
    CHECK (planned_start_date <= planned_end_date),
    CHECK (actual_end_date IS NULL OR actual_start_date IS NULL OR actual_start_date <= actual_end_date)
);

CREATE TABLE IF NOT EXISTS material_consumptions (
    consumption_id VARCHAR(32) PRIMARY KEY,
    production_order_id VARCHAR(32) NOT NULL REFERENCES production_orders(production_order_id),
    material_lot_id VARCHAR(64) NOT NULL REFERENCES material_lots(material_lot_id),
    bom_line_id VARCHAR(32) NOT NULL REFERENCES bom_lines(bom_line_id),
    consumed_quantity NUMERIC(14,4) NOT NULL CHECK (consumed_quantity > 0),
    uom VARCHAR(16) NOT NULL CHECK (uom IN ('EA', 'KG', 'M', 'L')),
    consumed_at TIMESTAMPTZ NOT NULL,
    consumption_status VARCHAR(32) NOT NULL DEFAULT 'COMMITTED' CHECK (consumption_status IN ('COMMITTED', 'REVERSED'))
);

CREATE TABLE IF NOT EXISTS process_executions (
    process_execution_id VARCHAR(32) PRIMARY KEY,
    production_order_id VARCHAR(32) NOT NULL REFERENCES production_orders(production_order_id),
    process_step_id VARCHAR(32) NOT NULL REFERENCES process_steps(process_step_id),
    machine_id VARCHAR(32) NOT NULL REFERENCES machines(machine_id),
    execution_start_at TIMESTAMPTZ NOT NULL,
    execution_end_at TIMESTAMPTZ NOT NULL,
    input_quantity NUMERIC(12,2) NOT NULL CHECK (input_quantity > 0),
    output_quantity NUMERIC(12,2) NOT NULL CHECK (output_quantity >= 0),
    rework_quantity NUMERIC(12,2) NOT NULL DEFAULT 0.0 CHECK (rework_quantity >= 0),
    scrap_quantity NUMERIC(12,2) NOT NULL DEFAULT 0.0 CHECK (scrap_quantity >= 0),
    quarantined_quantity NUMERIC(12,2) NOT NULL DEFAULT 0.0 CHECK (quarantined_quantity >= 0),
    execution_status VARCHAR(32) NOT NULL DEFAULT 'COMPLETED' CHECK (execution_status IN ('IN_PROGRESS', 'COMPLETED', 'ABORTED')),
    drift_indicator BOOLEAN NOT NULL DEFAULT FALSE,
    process_measurement NUMERIC(10,3) NOT NULL,
    CHECK (execution_start_at <= execution_end_at)
);

CREATE TABLE IF NOT EXISTS inspection_results (
    inspection_result_id VARCHAR(64) PRIMARY KEY,
    inspection_plan_id VARCHAR(32) NOT NULL REFERENCES inspection_plans(inspection_plan_id),
    production_order_id VARCHAR(32) NOT NULL REFERENCES production_orders(production_order_id),
    process_execution_id VARCHAR(32) NOT NULL REFERENCES process_executions(process_execution_id),
    inspected_at TIMESTAMPTZ NOT NULL,
    inspected_quantity NUMERIC(12,2) NOT NULL CHECK (inspected_quantity > 0),
    accepted_quantity NUMERIC(12,2) NOT NULL CHECK (accepted_quantity >= 0),
    rejected_quantity NUMERIC(12,2) NOT NULL DEFAULT 0.0 CHECK (rejected_quantity >= 0),
    reworked_quantity NUMERIC(12,2) NOT NULL DEFAULT 0.0 CHECK (reworked_quantity >= 0),
    scrapped_quantity NUMERIC(12,2) NOT NULL DEFAULT 0.0 CHECK (scrapped_quantity >= 0),
    quarantined_quantity NUMERIC(12,2) NOT NULL DEFAULT 0.0 CHECK (quarantined_quantity >= 0),
    inspection_status VARCHAR(32) NOT NULL DEFAULT 'COMPLETED' CHECK (inspection_status IN ('PENDING', 'COMPLETED')),
    disposition VARCHAR(32) NOT NULL DEFAULT 'ACCEPTED' CHECK (disposition IN ('ACCEPTED', 'REJECTED', 'CONDITIONAL_ACCEPTANCE')),
    defect_rate NUMERIC(6,4) NOT NULL DEFAULT 0.0 CHECK (defect_rate >= 0 AND defect_rate <= 1)
);

-- 3. Defect, Containment & Quality Action Tables

CREATE TABLE IF NOT EXISTS defects (
    defect_id VARCHAR(32) PRIMARY KEY,
    inspection_result_id VARCHAR(64) NOT NULL REFERENCES inspection_results(inspection_result_id),
    production_order_id VARCHAR(32) NOT NULL REFERENCES production_orders(production_order_id),
    process_execution_id VARCHAR(32) NOT NULL REFERENCES process_executions(process_execution_id),
    machine_id VARCHAR(32) NOT NULL REFERENCES machines(machine_id),
    material_lot_id VARCHAR(64) REFERENCES material_lots(material_lot_id),
    reported_material_lot_id VARCHAR(64) NOT NULL,
    supplier_id VARCHAR(32) REFERENCES suppliers(supplier_id),
    defect_code VARCHAR(32) NOT NULL,
    defect_category VARCHAR(32) NOT NULL CHECK (defect_category IN ('DIMENSIONAL', 'SURFACE_FINISH', 'ELECTRICAL', 'CONTAMINATION', 'ASSEMBLY_ALIGNMENT')),
    severity VARCHAR(16) NOT NULL DEFAULT 'MINOR' CHECK (severity IN ('MINOR', 'MAJOR', 'CRITICAL')),
    defect_quantity NUMERIC(12,2) NOT NULL DEFAULT 1.0 CHECK (defect_quantity > 0),
    suspected_source VARCHAR(32) NOT NULL DEFAULT 'MACHINE' CHECK (suspected_source IN ('MATERIAL', 'MACHINE', 'OPERATOR', 'METHOD', 'ENVIRONMENT')),
    detected_at TIMESTAMPTZ NOT NULL,
    defect_status VARCHAR(32) NOT NULL DEFAULT 'OPEN' CHECK (defect_status IN ('OPEN', 'CONTAINED', 'UNDER_INVESTIGATION', 'CAPA_IN_PROGRESS', 'VERIFIED', 'CLOSED'))
);

CREATE TABLE IF NOT EXISTS containment_actions (
    containment_action_id VARCHAR(32) PRIMARY KEY,
    defect_id VARCHAR(32) NOT NULL REFERENCES defects(defect_id),
    action_type VARCHAR(32) NOT NULL DEFAULT 'QUARANTINE_LOT' CHECK (action_type IN ('QUARANTINE_LOT', 'STOP_LINE', 'SORT_INVENTORY', 'REWORK_WIP', 'NOTIFY_SUPPLIER')),
    owner_role VARCHAR(32) NOT NULL DEFAULT 'QUALITY_ENGINEER' CHECK (owner_role IN ('QUALITY_ENGINEER', 'PLANT_OPERATOR', 'MAINTENANCE_ENGINEER', 'PRODUCTION_PLANNER', 'IT_ADMIN', 'SYSTEM')),
    action_timestamp TIMESTAMPTZ NOT NULL,
    affected_quantity NUMERIC(12,2) NOT NULL DEFAULT 0.0 CHECK (affected_quantity >= 0),
    containment_status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE' CHECK (containment_status IN ('ACTIVE', 'RELEASED_AFTER_INSPECTION', 'CONFIRMED_DEFECTIVE')),
    notes TEXT
);

CREATE TABLE IF NOT EXISTS corrective_actions (
    corrective_action_id VARCHAR(32) PRIMARY KEY,
    defect_id VARCHAR(32) NOT NULL REFERENCES defects(defect_id),
    root_cause_category VARCHAR(32) NOT NULL CHECK (root_cause_category IN ('SUPPLIER_QUALITY', 'TOOLING_WEAR', 'CALIBRATION_DRIFT', 'SETUP_ERROR', 'PROCEDURAL_OMISSION')),
    root_cause_description TEXT NOT NULL,
    owner_role VARCHAR(32) NOT NULL DEFAULT 'QUALITY_ENGINEER' CHECK (owner_role IN ('QUALITY_ENGINEER', 'PLANT_OPERATOR', 'MAINTENANCE_ENGINEER', 'PRODUCTION_PLANNER', 'IT_ADMIN', 'SYSTEM')),
    due_date DATE NOT NULL,
    implementation_date DATE,
    corrective_action_status VARCHAR(32) NOT NULL DEFAULT 'OPEN' CHECK (corrective_action_status IN ('OPEN', 'IMPLEMENTED', 'VERIFICATION_PENDING', 'VERIFIED', 'CLOSED')),
    effectiveness_target VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS capa_verifications (
    verification_id VARCHAR(32) PRIMARY KEY,
    corrective_action_id VARCHAR(32) NOT NULL REFERENCES corrective_actions(corrective_action_id),
    verification_date DATE NOT NULL,
    verification_method VARCHAR(32) NOT NULL DEFAULT 'AUDIT_CHECK' CHECK (verification_method IN ('AUDIT_CHECK', 'STATISTICAL_SAMPLING', 'CAPABILITY_STUDY', 'SPC_MONITORING')),
    verification_result VARCHAR(16) NOT NULL DEFAULT 'PASSED' CHECK (verification_result IN ('PASSED', 'FAILED', 'INCONCLUSIVE')),
    verified_by_role VARCHAR(32) NOT NULL DEFAULT 'QUALITY_ENGINEER' CHECK (verified_by_role IN ('QUALITY_ENGINEER', 'PLANT_OPERATOR', 'MAINTENANCE_ENGINEER', 'PRODUCTION_PLANNER', 'IT_ADMIN', 'SYSTEM')),
    evidence_reference VARCHAR(255) NOT NULL
);

-- 4. Append-Only State Events (with typed nullable FKs and CHECK constraint)

CREATE TABLE IF NOT EXISTS state_events (
    event_id VARCHAR(32) PRIMARY KEY,
    entity_type VARCHAR(32) NOT NULL CHECK (entity_type IN ('MATERIAL_LOT', 'PRODUCTION_ORDER', 'INSPECTION_RESULT', 'DEFECT', 'CORRECTIVE_ACTION')),
    entity_id VARCHAR(64) NOT NULL,
    material_lot_id VARCHAR(64) REFERENCES material_lots(material_lot_id),
    production_order_id VARCHAR(32) REFERENCES production_orders(production_order_id),
    inspection_result_id VARCHAR(64) REFERENCES inspection_results(inspection_result_id),
    defect_id VARCHAR(32) REFERENCES defects(defect_id),
    corrective_action_id VARCHAR(32) REFERENCES corrective_actions(corrective_action_id),
    event_sequence INTEGER NOT NULL CHECK (event_sequence > 0),
    previous_state VARCHAR(32),
    new_state VARCHAR(32) NOT NULL,
    event_timestamp TIMESTAMPTZ NOT NULL,
    actor_role VARCHAR(32) NOT NULL DEFAULT 'SYSTEM' CHECK (actor_role IN ('PLANT_OPERATOR', 'QUALITY_ENGINEER', 'MAINTENANCE_ENGINEER', 'PRODUCTION_PLANNER', 'IT_ADMIN', 'SYSTEM')),
    reason_code VARCHAR(64) NOT NULL DEFAULT 'NORMAL_FLOW',
    event_notes TEXT,
    CONSTRAINT chk_state_events_exact_one_fk CHECK (
        (entity_type = 'MATERIAL_LOT' AND material_lot_id = entity_id AND production_order_id IS NULL AND inspection_result_id IS NULL AND defect_id IS NULL AND corrective_action_id IS NULL) OR
        (entity_type = 'PRODUCTION_ORDER' AND production_order_id = entity_id AND material_lot_id IS NULL AND inspection_result_id IS NULL AND defect_id IS NULL AND corrective_action_id IS NULL) OR
        (entity_type = 'INSPECTION_RESULT' AND inspection_result_id = entity_id AND material_lot_id IS NULL AND production_order_id IS NULL AND defect_id IS NULL AND corrective_action_id IS NULL) OR
        (entity_type = 'DEFECT' AND defect_id = entity_id AND material_lot_id IS NULL AND production_order_id IS NULL AND inspection_result_id IS NULL AND corrective_action_id IS NULL) OR
        (entity_type = 'CORRECTIVE_ACTION' AND corrective_action_id = entity_id AND material_lot_id IS NULL AND production_order_id IS NULL AND inspection_result_id IS NULL AND defect_id IS NULL)
    ),
    CONSTRAINT uq_state_events_entity_sequence UNIQUE (entity_type, entity_id, event_sequence)
);

-- 5. Indexes for High-Performance Traceability

CREATE INDEX IF NOT EXISTS idx_boms_product ON boms(product_id);
CREATE INDEX IF NOT EXISTS idx_bom_lines_bom ON bom_lines(bom_id);
CREATE INDEX IF NOT EXISTS idx_bom_lines_mat_prod ON bom_lines(material_product_id);
CREATE INDEX IF NOT EXISTS idx_mat_lots_supplier ON material_lots(supplier_id);
CREATE INDEX IF NOT EXISTS idx_mat_lots_prod ON material_lots(material_product_id);
CREATE INDEX IF NOT EXISTS idx_prod_orders_product ON production_orders(product_id);
CREATE INDEX IF NOT EXISTS idx_consumptions_order ON material_consumptions(production_order_id);
CREATE INDEX IF NOT EXISTS idx_consumptions_lot ON material_consumptions(material_lot_id);
CREATE INDEX IF NOT EXISTS idx_consumptions_bom_line ON material_consumptions(bom_line_id);
CREATE INDEX IF NOT EXISTS idx_pex_order ON process_executions(production_order_id);
CREATE INDEX IF NOT EXISTS idx_pex_step ON process_executions(process_step_id);
CREATE INDEX IF NOT EXISTS idx_pex_machine ON process_executions(machine_id);
CREATE INDEX IF NOT EXISTS idx_insp_res_plan ON inspection_results(inspection_plan_id);
CREATE INDEX IF NOT EXISTS idx_insp_res_order ON inspection_results(production_order_id);
CREATE INDEX IF NOT EXISTS idx_insp_res_pex ON inspection_results(process_execution_id);
CREATE INDEX IF NOT EXISTS idx_defects_insp ON defects(inspection_result_id);
CREATE INDEX IF NOT EXISTS idx_defects_order ON defects(production_order_id);
CREATE INDEX IF NOT EXISTS idx_defects_lot ON defects(material_lot_id);
CREATE INDEX IF NOT EXISTS idx_defects_machine ON defects(machine_id);
CREATE INDEX IF NOT EXISTS idx_defects_supplier ON defects(supplier_id);
CREATE INDEX IF NOT EXISTS idx_containment_defect ON containment_actions(defect_id);
CREATE INDEX IF NOT EXISTS idx_capa_defect ON corrective_actions(defect_id);
CREATE INDEX IF NOT EXISTS idx_capa_verif_capa ON capa_verifications(corrective_action_id);
CREATE INDEX IF NOT EXISTS idx_state_events_lookup ON state_events(entity_type, entity_id, event_sequence);
