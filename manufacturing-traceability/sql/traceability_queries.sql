-- ==============================================================================
-- TraceFlow: Verified Traceability Queries
-- Purpose: Canonical production SQL queries for defect traceability,
--          blast-radius impact analysis, BOM reconciliation, and quality metrics.
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. Upstream Defect-to-Supplier Trace
-- Given a defect_id, traces backwards through inspection result, production order,
-- process execution, machine, consumed material lots, and upstream supplier.
-- ------------------------------------------------------------------------------
SELECT
    d.defect_id,
    d.defect_code,
    d.defect_category,
    d.severity,
    d.defect_status,
    d.defect_quantity,
    d.suspected_source,
    ir.inspection_result_id,
    ip.inspection_type,
    ir.disposition,
    po.production_order_id,
    po.product_id,
    p.product_name,
    pe.process_execution_id,
    ps.step_name,
    m.machine_id,
    m.machine_name,
    mc.consumption_id,
    mc.material_lot_id,
    ml.supplier_batch_code,
    ml.lot_status AS material_lot_status,
    s.supplier_id,
    s.supplier_name,
    s.supplier_risk_tier
FROM defects d
JOIN inspection_results ir ON d.inspection_result_id = ir.inspection_result_id
JOIN inspection_plans ip ON ir.inspection_plan_id = ip.inspection_plan_id
JOIN production_orders po ON d.production_order_id = po.production_order_id
JOIN products p ON po.product_id = p.product_id
LEFT JOIN process_executions pe ON d.process_execution_id = pe.process_execution_id
LEFT JOIN process_steps ps ON pe.process_step_id = ps.process_step_id
LEFT JOIN machines m ON d.machine_id = m.machine_id
LEFT JOIN material_consumptions mc ON po.production_order_id = mc.production_order_id
LEFT JOIN material_lots ml ON mc.material_lot_id = ml.material_lot_id
LEFT JOIN suppliers s ON ml.supplier_id = s.supplier_id
WHERE d.defect_id = 'DEF-2026-000001'
ORDER BY mc.consumed_at ASC;


-- ------------------------------------------------------------------------------
-- 2. Downstream Material-Lot Blast-Radius Impact Analysis
-- Given a suspect material_lot_id, identifies all production orders where this
-- lot was consumed, downstream products, process executions, and resulting defects.
-- ------------------------------------------------------------------------------
SELECT
    ml.material_lot_id,
    ml.supplier_id,
    s.supplier_name,
    ml.supplier_batch_code,
    ml.lot_status,
    mc.production_order_id,
    po.product_id,
    p.product_name,
    po.order_status,
    mc.consumed_quantity,
    mc.uom AS consumption_uom,
    mc.consumed_at,
    d.defect_id,
    d.defect_code,
    d.severity AS defect_severity,
    d.defect_status,
    ca.containment_action_id,
    ca.action_type AS containment_action,
    ca.containment_status
FROM material_lots ml
JOIN suppliers s ON ml.supplier_id = s.supplier_id
JOIN material_consumptions mc ON ml.material_lot_id = mc.material_lot_id
JOIN production_orders po ON mc.production_order_id = po.production_order_id
JOIN products p ON po.product_id = p.product_id
LEFT JOIN defects d ON po.production_order_id = d.production_order_id AND (d.material_lot_id = ml.material_lot_id OR d.material_lot_id IS NULL)
LEFT JOIN containment_actions ca ON d.defect_id = ca.defect_id
WHERE ml.material_lot_id = 'LOT-SUP-0003-2026-000063'
ORDER BY mc.consumed_at ASC;


-- ------------------------------------------------------------------------------
-- 3. Production Order BOM-Consumption Reconciliation
-- Compares required BOM quantities vs. actually consumed quantities for an order.
-- ------------------------------------------------------------------------------
WITH bom_requirements AS (
    SELECT
        po.production_order_id,
        bl.bom_line_id,
        bl.material_product_id,
        bl.quantity_per_unit,
        bl.scrap_factor,
        ROUND(po.planned_quantity * bl.quantity_per_unit * (1.0 + bl.scrap_factor), 4) AS expected_required_quantity,
        bl.uom
    FROM production_orders po
    JOIN boms b ON po.product_id = b.product_id AND b.status = 'ACTIVE'
    JOIN bom_lines bl ON b.bom_id = bl.bom_id
    WHERE po.production_order_id = 'WO-2026-000001'
),
actual_consumptions AS (
    SELECT
        mc.production_order_id,
        mc.bom_line_id,
        SUM(mc.consumed_quantity) AS total_consumed_quantity,
        COUNT(mc.consumption_id) AS consumption_records_count
    FROM material_consumptions mc
    WHERE mc.production_order_id = 'WO-2026-000001' AND mc.consumption_status = 'COMMITTED'
    GROUP BY mc.production_order_id, mc.bom_line_id
)
SELECT
    br.production_order_id,
    br.bom_line_id,
    br.material_product_id,
    p.product_name AS material_name,
    br.expected_required_quantity,
    COALESCE(ac.total_consumed_quantity, 0.0) AS actual_consumed_quantity,
    ROUND(COALESCE(ac.total_consumed_quantity, 0.0) - br.expected_required_quantity, 4) AS quantity_variance,
    CASE
        WHEN ac.total_consumed_quantity IS NULL THEN 'MISSING_CONSUMPTION'
        WHEN ABS(ac.total_consumed_quantity - br.expected_required_quantity) <= 0.01 THEN 'RECONCILED'
        ELSE 'VARIANCE_DETECTED'
    END AS reconciliation_status
FROM bom_requirements br
LEFT JOIN actual_consumptions ac ON br.bom_line_id = ac.bom_line_id
JOIN products p ON br.material_product_id = p.product_id
ORDER BY br.bom_line_id;


-- ------------------------------------------------------------------------------
-- 4. Machine & Process Defect Rate and Drift Analysis
-- Calculates defect occurrences, total executions, and defect rates by machine.
-- ------------------------------------------------------------------------------
SELECT
    m.machine_id,
    m.machine_name,
    m.machine_type,
    m.machine_status,
    m.maintenance_risk_score,
    COUNT(DISTINCT pe.process_execution_id) AS total_process_executions,
    COUNT(DISTINCT d.defect_id) AS total_defects_assigned,
    ROUND(
        COUNT(DISTINCT d.defect_id)::NUMERIC / NULLIF(COUNT(DISTINCT pe.process_execution_id), 0),
        4
    ) AS defect_rate_per_execution
FROM machines m
LEFT JOIN process_executions pe ON m.machine_id = pe.machine_id
LEFT JOIN defects d ON m.machine_id = d.machine_id
GROUP BY m.machine_id, m.machine_name, m.machine_type, m.machine_status, m.maintenance_risk_score
ORDER BY defect_rate_per_execution DESC NULLS LAST;


-- ------------------------------------------------------------------------------
-- 5. CAPAs Pending Verification & Closure Readiness
-- Lists corrective actions, checking whether a passing verification exists.
-- ------------------------------------------------------------------------------
SELECT
    ca.corrective_action_id,
    ca.defect_id,
    d.defect_code,
    ca.root_cause_category,
    ca.root_cause_description,
    ca.corrective_action_status,
    ca.owner_role,
    ca.due_date,
    COUNT(cv.verification_id) AS total_verifications,
    COUNT(CASE WHEN cv.verification_result = 'PASSED' THEN 1 END) AS passed_verifications_count,
    CASE
        WHEN COUNT(CASE WHEN cv.verification_result = 'PASSED' THEN 1 END) > 0 THEN 'READY_FOR_CLOSURE'
        WHEN ca.corrective_action_status = 'CLOSED' AND COUNT(CASE WHEN cv.verification_result = 'PASSED' THEN 1 END) = 0 THEN 'PREMATURE_CLOSURE_ANOMALY'
        ELSE 'VERIFICATION_REQUIRED'
    END AS closure_compliance_status
FROM corrective_actions ca
JOIN defects d ON ca.defect_id = d.defect_id
LEFT JOIN capa_verifications cv ON ca.corrective_action_id = cv.corrective_action_id
GROUP BY ca.corrective_action_id, ca.defect_id, d.defect_code, ca.root_cause_category, ca.root_cause_description, ca.corrective_action_status, ca.owner_role, ca.due_date
ORDER BY ca.corrective_action_id;


-- ------------------------------------------------------------------------------
-- 6. Audit Trail: State Event History for an Entity
-- Displays the append-only event sequence for a given entity.
-- ------------------------------------------------------------------------------
SELECT
    se.event_id,
    se.entity_type,
    se.entity_id,
    se.event_sequence,
    se.previous_state,
    se.new_state,
    se.reason_code,
    se.actor_role,
    se.event_timestamp
FROM state_events se
WHERE se.entity_type = 'CORRECTIVE_ACTION' AND se.corrective_action_id = 'CAPA-2026-000001'
ORDER BY se.event_sequence ASC;
