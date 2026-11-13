import json
import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.validators.integrity_checker import ValidationEngine

router = APIRouter(prefix="/validation", tags=["Data Integrity & Validation"])

REPORTS_FILE = os.path.join(
    os.getenv("ARTIFACTS_DIR", "/app/artifacts"), "reports", "validation_summary.json"
)


@router.get("/reports")
def get_validation_report():
    """Retrieve the deterministic data integrity validation report."""
    if os.path.exists(REPORTS_FILE):
        with open(REPORTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "status": "NO_REPORT_FOUND",
        "message": "Validation report has not been generated yet. Use POST /api/v1/validation/run.",
    }


@router.post("/run")
def run_validation(db: Session = Depends(get_db)):
    """Execute live integrity checks and return validation outcome."""
    artifacts_dir = os.getenv("ARTIFACTS_DIR", "/app/artifacts")
    data_dir = os.path.join(artifacts_dir, "json")

    # Load from disk if available
    datasets = {}
    if os.path.exists(data_dir):
        for fname in os.listdir(data_dir):
            if fname.endswith(".json"):
                tbl_name = fname[:-5]
                with open(os.path.join(data_dir, fname), "r", encoding="utf-8") as f:
                    datasets[tbl_name] = json.load(f)

    if not datasets:
        raise HTTPException(
            status_code=500,
            detail="Seeded JSON dataset files not found in artifacts directory.",
        )

    checker = ValidationEngine(datasets)
    report = checker.run_all_checks()
    return report
