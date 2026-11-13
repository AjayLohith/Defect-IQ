"""Frontend Critical-Path Smoke Test Suite.
Validates the live web reverse proxy (Nginx on web:80) and all critical UI paths:
1. Dashboard metrics (5000 orders, 20000 inspections)
2. Upstream Defect Trace (traversal across order, step, machine, and consumed material lots)
3. Downstream Lot Impact (blast radius analysis across affected production orders)
4. BOM Reconciliation (detecting missing consumption anomaly)
5. CAPA Verification & Closure Rejection (HTTP 422 on unverified closure)
6. Validation Report View (retrieving 11 passed rules and 5 detected anomalies)
"""
import urllib.request
import json
import urllib.error

BASE = "http://web/api/v1"

def get(path):
    req = urllib.request.Request(f"{BASE}{path}")
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode())

def post(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(f"{BASE}{path}", data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())

def run_all_smoke_tests():
    print("=== Starting Frontend Critical-Path Smoke Tests ===")
    
    # 1. Dashboard Metrics
    print("1. Testing Dashboard Metrics via Nginx Web Proxy...")
    status, data = get("/dashboard/metrics")
    print(f"   Status: {status}")
    print(f"   Total Orders: {data.get('total_production_orders')}")
    print(f"   Total Inspections: {data.get('total_inspections')}")
    print(f"   Total Defects: {data.get('total_defects')}")
    assert status == 200, f"Expected 200, got {status}"
    assert data.get("total_production_orders") == 5000, f"Expected 5000 orders, got {data.get('total_production_orders')}"
    assert data.get("total_inspections") == 20000, f"Expected 20000 inspections, got {data.get('total_inspections')}"
    print("   -> PASS: Dashboard metrics reflect full 5000 orders and 20000 inspections.")

    # 2. Upstream Defect Trace (using DEF-2026-000002 which has linked consumed lots)
    print("2. Testing Upstream Defect Trace for DEF-2026-000002...")
    status, data = get("/traceability/upstream/DEF-2026-000002")
    consumed_lots = data.get("consumed_lots") or []
    print(f"   Status: {status}, Defect: {data.get('defect_id')}")
    print(f"   Order: {data.get('production_order_id')}, Product: {data.get('product_name')}")
    print(f"   Machine: {data.get('machine_name')}, Consumed Lots Count: {len(consumed_lots)}")
    assert status == 200
    assert data.get("defect_id") == "DEF-2026-000002"
    assert data.get("production_order_id") == "WO-2026-000003"
    assert len(consumed_lots) > 0
    print("   -> PASS: Upstream defect trace accurately traversed order and consumed material lots.")

    # 3. Downstream Lot Impact (Blast Radius)
    print("3. Testing Downstream Lot Impact for LOT-SUP-0004-2026-001104...")
    status, data = get("/traceability/downstream/LOT-SUP-0004-2026-001104")
    impacted = data.get("impacted_orders") or []
    print(f"   Status: {status}, Lot: {data.get('material_lot_id')}, Total Impacted Orders: {data.get('total_impacted_orders')}")
    assert status == 200
    assert data.get("material_lot_id") == "LOT-SUP-0004-2026-001104"
    assert data.get("total_impacted_orders") == len(impacted)
    print("   -> PASS: Downstream blast radius analysis correctly evaluated affected orders.")

    # 4. BOM Reconciliation
    print("4. Testing BOM Reconciliation for Order WO-2026-000001...")
    status, data = get("/orders/WO-2026-000001/bom-reconciliation")
    items = data.get("items") or []
    missing_lines = [l for l in items if l.get("reconciliation_status") == "MISSING_CONSUMPTION"]
    print(f"   Status: {status}, Total BOM lines: {len(items)}, Missing lines: {len(missing_lines)}")
    assert status == 200
    assert len(items) == 3
    assert len(missing_lines) == 1
    assert missing_lines[0].get("bom_line_id") == "BOML-000001"
    print("   -> PASS: BOM reconciliation accurately detected missing consumption anomaly on BOML-000001.")

    # 5. CAPA Verification & Closure Rejection
    print("5. Testing CAPA Closure Rejection on Unverified CAPA-2026-000725...")
    status, err = post("/capas/CAPA-2026-000725/close", {
        "closure_comments": "Attempting closure without verification",
        "actor_role": "QUALITY_ENGINEER"
    })
    detail = err.get("detail") or {}
    print(f"   Status: {status}, Detail: {detail}")
    assert status == 422, f"Expected 422, got {status}"
    assert detail.get("code") == "ERR_CAPA_VERIFICATION_REQUIRED"
    print("   -> PASS: CAPA closure strictly rejected unverified closure with HTTP 422 ERR_CAPA_VERIFICATION_REQUIRED.")

    # 6. Validation Reports View
    print("6. Testing Validation Reports Endpoint...")
    status, data = get("/validation/reports")
    summary = data.get("summary") or {}
    print(f"   Status: {status}, Total Rules: {summary.get('total_rules')}, Passed: {summary.get('passed_rules')}, Anomalies: {summary.get('anomalies_detected')}")
    assert status == 200
    assert summary.get("passed_rules") == 11
    assert summary.get("failed_rules") == 0
    assert summary.get("anomalies_detected") == 5
    print("   -> PASS: Validation reports accurately returned 11 passed rules and 5 detected anomalies.")

    print("\n=== ALL CRITICAL-PATH FRONTEND SMOKE TESTS PASSED (6/6) ===")

if __name__ == "__main__":
    run_all_smoke_tests()
