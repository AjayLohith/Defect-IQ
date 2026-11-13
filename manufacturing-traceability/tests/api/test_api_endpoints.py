"""API tests verifying endpoints, contracts, CAPA verification enforcement, and ground-truth segregation."""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Verify system health and deterministic engine metadata."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "traceflow-api"
    assert data["seed"] == 20261022


def test_dashboard_metrics():
    """Verify quality dashboard metrics aggregation."""
    response = client.get("/api/v1/dashboard/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "total_production_orders" in data
    assert "total_defects" in data
    assert "overall_defect_rate" in data
    assert "defects_by_severity" in data
    assert "defects_by_category" in data
    assert "top_risk_machines" in data
    assert data["total_production_orders"] >= 200
    assert data["total_defects"] >= 32


def test_machine_drift():
    """Verify machine drift defect rate calculations."""
    response = client.get("/api/v1/dashboard/drift")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    first = data[0]
    assert "machine_id" in first
    assert "defect_rate" in first
    assert "maintenance_risk_score" in first


def test_defects_listing_and_detail():
    """Verify defect listing, filtering, and detail endpoints."""
    # List all defects
    response = client.get("/api/v1/defects?limit=10")
    assert response.status_code == 200
    defects = response.json()
    assert len(defects) > 0

    first_defect_id = defects[0]["defect_id"]

    # Verify ground_truth_label is strictly NOT present in operational defect response
    assert "ground_truth_label" not in defects[0]

    # Get single defect details
    detail_res = client.get(f"/api/v1/defects/{first_defect_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["defect_id"] == first_defect_id
    assert "product_name" in detail
    assert "machine_name" in detail
    assert "ground_truth_label" not in detail


def test_upstream_traceability():
    """Verify backward defect-to-supplier traceability graph."""
    response = client.get("/api/v1/traceability/upstream/DEF-2026-000001")
    assert response.status_code == 200
    trace = response.json()
    assert trace["defect_id"] == "DEF-2026-000001"
    assert "product_id" in trace
    assert "machine_id" in trace
    assert "consumed_lots" in trace
    assert isinstance(trace["consumed_lots"], list)
    if trace["consumed_lots"]:
        lot = trace["consumed_lots"][0]
        assert "material_lot_id" in lot
        assert "supplier_name" in lot
        assert "supplier_batch_code" in lot


def test_downstream_blast_radius():
    """Verify forward material-lot blast-radius impact analysis."""
    # First get a material lot ID
    lots_res = client.get("/api/v1/lots?limit=5")
    assert lots_res.status_code == 200
    lots = lots_res.json()
    assert len(lots) > 0
    lot_id = lots[0]["material_lot_id"]

    response = client.get(f"/api/v1/traceability/downstream/{lot_id}")
    assert response.status_code == 200
    impact = response.json()
    assert impact["material_lot_id"] == lot_id
    assert "impacted_orders" in impact
    assert "total_impacted_orders" in impact


def test_production_order_bom_reconciliation():
    """Verify order BOM reconciliation and anomaly detection."""
    # WO-2026-000001 contains the deliberate missing BOM consumption anomaly
    response = client.get("/api/v1/orders/WO-2026-000001/bom-reconciliation")
    assert response.status_code == 200
    report = response.json()
    assert report["production_order_id"] == "WO-2026-000001"
    assert len(report["items"]) > 0

    statuses = [item["reconciliation_status"] for item in report["items"]]
    # Should flag MISSING_CONSUMPTION on the anomalous BOM line
    assert "MISSING_CONSUMPTION" in statuses
    assert report["is_fully_reconciled"] is False


def test_capa_closure_verification_enforcement():
    """
    STRICT BUSINESS RULE TEST:
    CAPA closure must always fail if no passed verification exists (HTTP 422 ERR_CAPA_VERIFICATION_REQUIRED).
    """
    # 1. Create a new CAPA
    capa_payload = {
        "defect_id": "DEF-2026-000001",
        "root_cause_category": "TOOLING_WEAR",
        "root_cause_description": "Cutting tool micro-chipping caused surface roughness.",
        "owner_role": "QUALITY_ENGINEER",
        "due_date": "2026-12-31",
        "effectiveness_target": "Zero surface finish defects across next 5 production runs",
    }
    create_res = client.post("/api/v1/capas", json=capa_payload)
    assert create_res.status_code == 201
    capa = create_res.json()
    capa_id = capa["corrective_action_id"]

    # 2. Attempt to close immediately without verification -> MUST FAIL WITH 422
    close_attempt = client.post(
        f"/api/v1/capas/{capa_id}/close",
        json={"actor_role": "QUALITY_ENGINEER", "closure_notes": "Attempt premature closure"},
    )
    assert close_attempt.status_code == 422
    err_detail = close_attempt.json()["detail"]
    assert err_detail["code"] == "ERR_CAPA_VERIFICATION_REQUIRED"

    # 3. Add a FAILED verification -> Closure must still fail
    fail_verif = {
        "verification_date": "2026-11-20",
        "verification_method": "AUDIT_CHECK",
        "verification_result": "FAILED",
        "verified_by_role": "QUALITY_ENGINEER",
        "evidence_reference": "DOC-AUDIT-FAILED-001",
    }
    verif_res1 = client.post(f"/api/v1/capas/{capa_id}/verifications", json=fail_verif)
    assert verif_res1.status_code == 201

    close_attempt2 = client.post(
        f"/api/v1/capas/{capa_id}/close",
        json={"actor_role": "QUALITY_ENGINEER", "closure_notes": "Attempt closure after failure"},
    )
    assert close_attempt2.status_code == 422

    # 4. Add a PASSED verification
    pass_verif = {
        "verification_date": "2026-11-25",
        "verification_method": "STATISTICAL_SAMPLING",
        "verification_result": "PASSED",
        "verified_by_role": "QUALITY_ENGINEER",
        "evidence_reference": "DOC-AUDIT-PASSED-002",
    }
    verif_res2 = client.post(f"/api/v1/capas/{capa_id}/verifications", json=pass_verif)
    assert verif_res2.status_code == 201

    # 5. Now close the CAPA -> MUST SUCCEED
    close_res = client.post(
        f"/api/v1/capas/{capa_id}/close",
        json={"actor_role": "QUALITY_ENGINEER", "closure_notes": "Formally closed after valid verification"},
    )
    assert close_res.status_code == 200
    closed_capa = close_res.json()
    assert closed_capa["corrective_action_status"] == "CLOSED"


def test_ground_truth_isolation():
    """
    Authoritative ground truth must NOT be exposed via administrative API
    or normal operational defect payloads.
    """
    # 1. Admin ground truth endpoint must return 404 (not present)
    gt_res = client.get("/api/v1/admin/ground-truth")
    assert gt_res.status_code == 404

    # 2. Defect list must never contain ground_truth_label
    defects_res = client.get("/api/v1/defects")
    for d in defects_res.json():
        assert "ground_truth_label" not in d

