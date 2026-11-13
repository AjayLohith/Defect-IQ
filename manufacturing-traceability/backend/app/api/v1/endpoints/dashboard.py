from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.repositories.metrics_repo import MetricsRepository
from backend.app.schemas.dashboard import QualityMetrics, MachineDriftMetric

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/metrics", response_model=QualityMetrics)
def get_dashboard_metrics(db: Session = Depends(get_db)):
    """Retrieve top-level quality metrics, defect distributions, and high-risk machines."""
    repo = MetricsRepository(db)
    return repo.get_quality_metrics()


@router.get("/drift", response_model=List[MachineDriftMetric])
def get_machine_drift(db: Session = Depends(get_db)):
    """Retrieve machine execution counts, defect rates, and drift indicators."""
    repo = MetricsRepository(db)
    return repo.get_machine_drift_metrics()

