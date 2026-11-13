# Manufacturing Defect-Traceability Validation Summary Report

**Validation Status**: PASSED

- Total Rules Checked: 11
- Passed Rules: 11
- Failed Baseline Rules: 0
- Deliberate Anomalies Detected: 5 / 5

## 1. Rule Checklist

| Rule ID | Status | Error Count | Details |
|---|---|---|---|
| `VAL_BOM_NON_OVERLAP` | PASSED | 0 | None |
| `VAL_DATE_ORDERING` | PASSED | 0 | None |
| `VAL_DEFECT_RATE_CALCULATION` | PASSED | 0 | None |
| `VAL_FOREIGN_KEYS` | PASSED | 0 | None |
| `VAL_INSPECTION_RECONCILIATION` | PASSED | 0 | None |
| `VAL_LOT_BALANCE_RECONCILIATION` | PASSED | 0 | None |
| `VAL_MACHINE_COMPATIBILITY` | PASSED | 0 | None |
| `VAL_ORDER_QUANTITY_RECONCILIATION` | PASSED | 0 | None |
| `VAL_PRIMARY_KEYS` | PASSED | 0 | None |
| `VAL_REQUIRED_FIELDS` | PASSED | 0 | None |
| `VAL_STATE_EVENT_INTEGRITY` | PASSED | 0 | None |

## 2. Injected Anomalies Detected

| Anomaly ID | Classification | Entity Type | Entity ID | Detection Rule |
|---|---|---|---|---|
| `ANOMALY-001` | `NONEXISTENT_REPORTED_LOT` | `DEFECT` | `DEF-2026-000001` | `VAL_DEFECT_REPORTED_LOT_EXISTS` |
| `ANOMALY-002` | `MISSING_BOM_CONSUMPTION` | `PRODUCTION_ORDER` | `WO-2026-000001` | `VAL_ORDER_BOM_CONSUMPTION_COMPLETE` |
| `ANOMALY-003` | `PREMATURE_CAPA_CLOSURE` | `CORRECTIVE_ACTION` | `CAPA-2026-000005` | `VAL_CAPA_CLOSURE_REQUIRES_VERIFICATION` |
| `ANOMALY-004` | `DEFECT_QUANTITY_EXCEEDS_INSPECTED` | `DEFECT` | `DEF-2026-000002` | `VAL_DEFECT_QUANTITY_LE_INSPECTED` |
| `ANOMALY-005` | `BROKEN_TRACEABILITY_CHAIN` | `DEFECT` | `DEF-2026-000003` | `VAL_DEFECT_PROCESS_EXECUTION_ORDER_MATCH` |

*Report generated deterministically by validation engine.*